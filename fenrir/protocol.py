# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio

from asyncio.streams import FlowControlMixin

from fenrir.http.errors import HTTPError, BadRequest
from fenrir.http.req import Request
from fenrir.queues import CloseableQueue


class HTTPProtocol(FlowControlMixin, asyncio.Protocol):

    def __init__(self, app, loop=None):
        super().__init__(loop=loop)

        self.writer = None
        self.reader = None

        self.app = app

    def connection_made(self, transport):
        # Create a reader which we'll use to handle reading from our stream,
        # this will help us handle applying back pressure to prevent us from
        # filling our queues too much.
        self.reader = asyncio.StreamReader(loop=self._loop)
        self.reader.set_transport(transport)

        # Create a writer which we'll use to handle writing to our stream, this
        # will help us handle applying back pressure to prevent us from filling
        # our queues too much.
        self.writer = asyncio.StreamWriter(
            transport, self, self.reader, self._loop,
        )

        # Create a FIFO queue to hold all of our requests as we process them
        # TODO: Is there a maximum size we want this queue to be? The
        #       data_recieved event can block waiting for an empty spot in the
        #       queue.
        req_q = CloseableQueue(loop=self._loop)

        # Schedule our two coroutines which will handle processing incoming
        # data, dispatching it to the underlying application, and then writing
        # the data back out to the transport.
        asyncio.async(self.process_data(self.reader, req_q), loop=self._loop)
        asyncio.async(
            self.process_responses(self.writer, req_q),
            loop=self._loop,
        )

    def connection_lost(self, exc):
        if exc is None:
            self.reader.feed_eof()
        else:
            self.reader.set_exception(exc)

        super().connection_lost(exc)

    def data_received(self, data):
        self.reader.feed_data(data)

    def eof_received(self):
        self.reader.feed_eof()

    @asyncio.coroutine
    def process_data(self, reader, requests):
        try:
            while not reader.at_eof() and not requests.closed:
                request = Request(body=asyncio.StreamReader(loop=self._loop))
                request_queued = False

                while (not request.received
                        and not (reader.at_eof()
                                 and not request.headers_complete)):
                    try:
                        # TODO: What is the best size chunk to read here? What
                        #       will happen if there isn't enough data in the
                        #       buffer to read all of the data we've requested?
                        request.add_bytes((yield from reader.read(4096)))
                    except BadRequest as exc:
                        # We've gotten a bad request. We're going to stop
                        # processing requests and close our queue after putting
                        # our BadRequest onto the queue.
                        yield from requests.put(exc)
                        requests.close()
                        break

                    # If we've finished our headers, then go ahead and add our
                    # item to our request queue so that our writer coroutine
                    # can pull them off and write the responses
                    if not request_queued and request.headers_complete:
                        request_queued = True
                        yield from requests.put(request)

                        # Determine if we need to stop processing requests on
                        # this connection because the client either doesn't
                        # support HTTP/1.1 or has signaled to use that they are
                        # closing the connection after this request/response.
                        # TODO: We need to parse this so that we support
                        #       multiple connection options.
                        if (request.http_version == b"HTTP/1.0"
                            or request.headers.get(b"Connection", None)
                                == b"close"):
                            requests.close()

                    # If we're in the body portion of our request and we've
                    # received an EOF then we should feed an EOF into our body
                    # and break out of this loop. We do not mark the request
                    # as received because HTTP/1.1 provides mechanisms other
                    # than connection close for determining if a request is
                    # finished.
                    if request.headers_complete and reader.at_eof():
                        request.body.feed_eof()
                        break
        finally:
            # Once we've received all of our data and processed it we want to
            # close our queue so that our process_responses coroutine will know
            # to shutdown.
            requests.close()

    @asyncio.coroutine
    def process_responses(self, writer, requests):
        try:
            while not requests.closed or not requests.empty():
                # Get the next request off the queue, blocking until one is
                # available.
                try:
                    request = yield from asyncio.wait_for(requests.get(), 5.0)
                except asyncio.TimeoutError:
                    # If we've been waiting for longer than our timeout then
                    # we'll just continue on in our loop. This provides a
                    # chance for the while loop to be reevaluated.
                    continue

                # Determine if we've gotten an actual request, or if we've
                # gotten and HTTPError.
                if isinstance(request, HTTPError):
                    # Since we've gotten an HTTPError instead of a request, we
                    # want to just use that as a response instead of actually
                    # trying to call our app function.
                    status, resp_headers, body = request.as_response()
                else:
                    # Now that we have a request, we'll want to dispatch to our
                    # app.
                    status, resp_headers, body = (
                        yield from self.app(*request.as_params())
                    )

                # Write out the status line to the client for this request
                writer.write(request.http_version + b" " + status + b"\r\n")

                # If this is our last request (e.g. the queue is closed and
                # empty), then we want to add a Connection: close header.
                if requests.closed and requests.empty():
                    writer.write(b"Connection: close\r\n")

                # Write out the headers, taking special care to ensure that any
                # mandatory headers are added.
                # TODO: We need to handle some required headers
                for key, values in resp_headers.items():
                    # In order to handle headers which need to have multiple
                    # values like Set-Cookie, we allow the value of the header
                    # to be an iterable instead of a bytes object, in which
                    # case we'll write multiple header lines for this header.
                    if isinstance(values, (bytes, bytearray)):
                        values = [values]

                    for value in values:
                        writer.write(key + b": " + value + b"\r\n")

                # We need to figure out our content length, unless the
                # application has already provided it, in which case we'll just
                # use it outright.
                if b"Content-Length" in resp_headers:
                    content_length = int(resp_headers[b"Content-Length"])
                else:
                    # TODO: We need to handle the case where the iterable may
                    #       not have a defined length. This will be treated
                    #       similarly to a len() > 1.
                    if len(body) == 0:
                        # If an empty response was provided, then we have no
                        # content and our Content-Length is 0
                        content_length = 0
                    elif len(body) == 1:
                        # If we have only one item in our iterable, then we can
                        # simply get it, resolving it if it is a coroutine, and
                        # then see how long it is to determine the
                        # Content-Length
                        chunk = next(iter(body))
                        if asyncio.iscoroutine(chunk):
                            chunk = yield from chunk

                        content_length = len(chunk)
                        body = [chunk]
                    else:
                        # We have no way of knowing what the content-length of
                        # the response is. We need to close this connection
                        # after this response has been processed unless the
                        # client supports Transfer-Encoding: chunked. This will
                        # throw away any requests that we have queued and
                        # haven't processed yet. To handle this we need to
                        # close our queue to prevent adding any more items and
                        # then throw away any of the items we have left in the
                        # queue.
                        # TODO: Implement Transfer-Encoding: chunked
                        requests.close()
                        while not requests.empty():
                            requests.get_nowait()
                        writer.write(b"Connection: close\r\n")
                        content_length = None

                    if content_length is not None:
                        writer.write(
                            b"Content-Length: " +
                            str(content_length).encode("ascii") +
                            b"\r\n"
                        )

                # Before we get to the body, we need to write a blank line to
                # separate the headers and the response body
                writer.write(b"\r\n")

                # Drain the buffer before proceeding, this will ensure that the
                # transport has handled our writes and we're safe to continue
                # processing.
                yield from writer.drain()

                for chunk in body:
                    # If the chunk is a coroutine, then we want to wait for the
                    # result before we write it.
                    if asyncio.iscoroutine(chunk):
                        chunk = yield from chunk

                    # Write our chunk out to the connected client and drain our
                    # buffer again to ensure the transport is ready for more.
                    writer.write(chunk)
                    yield from writer.drain()
        finally:
            writer.close()


class HTTPServer:

    protocol_class = HTTPProtocol

    def __init__(self, app, loop=None):
        self.app = app
        self.loop = None

    def __call__(self):
        return self.protocol_class(self.app, loop=self.loop)
