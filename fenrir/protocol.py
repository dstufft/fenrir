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
from fenrir.http.parser import HTTPParser, ParserError
from fenrir.http.request import Request
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
                parser = None
                while ((parser is None or not parser.finished)
                        and not reader.at_eof()):
                    # TODO: Do we need to handle the case where
                    #       reader.readline() returns more than the parser
                    #       wants to parse?
                    data = yield from reader.readline()

                    # If we have no data there's no point in try to process it
                    if not data:
                        continue

                    # Lazily create our parser, this will prevent us from
                    # allocating the memory for it unless we actually need
                    # it. This is important because if the EOF doesn't get sent
                    # until after we've called readline() then we don't want to
                    # create a HTTPParser instance until we have actual data
                    # to parse with it.
                    if parser is None:
                        parser = HTTPParser()

                    try:
                        parsed = parser.parse(data)
                    except ParserError:
                        raise BadRequest from None
                    assert parsed == len(data)

                # We have no data parsed, so there is nothing to process so we
                # just continue the loop again.
                if parser is None:
                    continue
                # If we've reached the EOF and our parser is not complete then
                # we have an incomplete request and we should close our Queue.
                elif not parser.finished:
                    raise BadRequest

                # We've pulled out the metadata related to the request now, we
                # can create a Request object to hold it.
                request = Request(
                    parser.http_version,
                    parser.method,
                    parser.path,
                    parser.query,
                    parser.headers,
                    asyncio.StreamReader(loop=self._loop),
                )

                # Queue our request for processing
                yield from requests.put(request)

                # Read the request body off the wire and feed it into our
                # request object.
                received = 0
                body_length = int(
                    next(iter(request.headers.get(b"Content-Length", [])), 0)
                )
                while received < body_length and not reader.at_eof():
                    # Grab up to the maximum size of our body from the wire
                    data = yield from reader.read(body_length - received)

                    # Feed whatever data we've gotten into our request body
                    request.body.feed_data(data)
                    received += len(data)

                # Either we've received all of our body data or our reader is
                # at EOF, in either case we want to feed an EOF to our request
                # body.
                request.body.feed_eof()

                # Determine if we need to stop processing requests on this
                # connection because the client either doesn't support
                # HTTP/1.1+ or has signaled to use that they are closing the
                # connection after this request/response.
                if reader.at_eof():
                    requests.close()
                elif request.http_version == b"HTTP/1.0":
                    requests.close()
                elif b"close" in request.headers.get(b"Connection", []):
                    requests.close()

        except BadRequest as exc:
            yield from requests.put(exc)
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
                    request = yield from asyncio.wait_for(
                        requests.get(),
                        5.0,
                        loop=self._loop,
                    )
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

                # If this is our last request (e.g. the queue is closed and
                # empty), then we want to add a Connection: close header.
                should_close = requests.closed and requests.empty()

                # Write out the status line to the client for this request
                writer.write(request.http_version + b" " + status + b"\r\n")

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
                        should_close = True
                        content_length = None

                # If we should close this connection, then we'll add the header
                # that states that.
                if should_close:
                    writer.write(b"Connection: close\r\n")

                # If we have a Content-Length, then we'll write out that header
                if content_length is not None:
                    writer.write(
                        b"Content-Length: " +
                        str(content_length).encode("ascii") +
                        b"\r\n"
                    )

                # Write out the headers, taking special care to ensure that any
                # mandatory headers are added.
                for key, values in resp_headers.items():
                    # We need to skip the Content-Length header because we
                    # have written it out already.
                    if key in {b"Content-Length"}:
                        continue

                    # In order to handle headers which need to have multiple
                    # values like Set-Cookie, we allow the value of the header
                    # to be an iterable instead of a bytes object, in which
                    # case we'll write multiple header lines for this header.
                    if isinstance(values, (bytes, bytearray)):
                        values = [values]

                    # Special case Set-Cookie because it cannot be collapsed
                    # normally, by joining with commas.
                    if key.lower() == b"set-cookie":
                        for value in values:
                            writer.write(key + b": " + value + b"\r\n")
                    else:
                        writer.write(key + b": " + b",".join(values) + b"\r\n")

                # Before we get to the body, we need to write a blank line to
                # separate the headers and the response body
                writer.write(b"\r\n")

                # Drain the buffer before proceeding, this will ensure that the
                # transport has handled our writes and we're safe to continue
                # processing.
                yield from writer.drain()

                body_written = 0
                for chunk in body:
                    # If we've already written the entire declared body size,
                    # assuming we had one, then we can break out of this loop
                    # to prevent us from the extra processing.
                    if (content_length is not None
                            and body_written >= content_length):
                        break

                    # If the chunk is a coroutine, then we want to wait for the
                    # result before we write it.
                    if asyncio.iscoroutine(chunk):
                        chunk = yield from chunk

                    # We want to ensure we do not write more than we said we
                    # would in our content length, assuming we have a content
                    # length.
                    if (content_length is not None
                            and body_written + len(chunk) > content_length):
                        chunk = chunk[:content_length - body_written]
                    body_written += len(chunk)

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
