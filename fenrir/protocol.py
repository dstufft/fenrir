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

from fenrir.http import Request
from fenrir.queues import CloseableQueue


class HTTPProtocol(FlowControlMixin, asyncio.Protocol):

    def __init__(self, callback, loop=None):
        super().__init__(loop=loop)
        self._writer = None
        self._reader = None

        self._callback = callback

        self._server = None

    def connection_made(self, transport):
        # Stash our transport so we can use it later.
        self._transport = transport

        # Create a reader which we'll use to handle reading from our stream,
        # this will help us handle applying back pressure to prevent us from
        # filling our queues too much.
        self._reader = asyncio.StreamReader(loop=self._loop)
        self._reader.set_transport(self._transport)

        # Create a writer which we'll use to handle writing to our stream, this
        # will help us handle applying back pressure to prevent us from filling
        # our queues too much.
        self._writer = asyncio.StreamWriter(
            self._transport, self, self._reader, self._loop,
        )

        # Grab the name of our socket if we have it
        self._server = self._transport.get_extra_info("sockname")

        # Create a FIFO queue to hold all of our requests as we process them
        # TODO: Is there a maximum size we want this queue to be? The
        #       data_recieved event can block waiting for an empty spot in the
        #       queue.
        req_q = CloseableQueue(loop=self._loop)

        # Schedule our two coroutines which will handle processing incoming
        # data, dispatching it to the underlying application, and then writing
        # the data back out to the transport.
        asyncio.async(self.process_data(self._reader, req_q), loop=self._loop)
        asyncio.async(
            self.process_responses(self._writer, req_q),
            loop=self._loop,
        )

    def connection_lost(self, exc):
        if exc is None:
            self._reader.feed_eof()
        else:
            self._reader.set_exception(exc)

        super().connection_lost(exc)

    def data_received(self, data):
        self._reader.feed_data(data)

    def eof_received(self):
        self._reader.feed_eof()

    @asyncio.coroutine
    def process_data(self, reader, requests):
        try:
            final_request = False
            while not reader.at_eof() and not final_request:
                request = Request(body=asyncio.StreamReader(loop=self._loop))
                request_queued = False

                while (not request.received
                        and not (reader.at_eof()
                                 and not request.headers_complete)):
                    # TODO: What is the best size chunk to read here? What will
                    #       happen if there isn't enough data in the buffer to
                    #       read all of the data we've requested?
                    request.add_bytes((yield from reader.read(4096)))

                    # If we've finished our headers, then go ahead and add our
                    # item to our request queue so that our writer coroutine
                    # can pull them off and write the responses
                    if not request_queued and request.headers_complete:
                        # Determine if we need to stop processing requests on
                        # this connection because the client either doesn't
                        # support HTTP/1.1 or has signaled to use that they are
                        # closing the connection after this request/response.
                        # TODO: We need to parse this so that we support
                        #       multiple connection options.
                        if (request.http_version == b"HTTP/1.0"
                            or request.headers.get(b"Connection", None)
                                == b"close"):
                            final_request = True

                        request_queued = True
                        yield from requests.put(request)

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
        # TODO: How do we know when we need to close the connection?
        try:
            while not requests.closed and not requests.empty():
                # Get the next request off the queue, blocking until one is
                # available.
                try:
                    request = yield from asyncio.wait_for(requests.get(), 5.0)
                except asyncio.TimeoutError:
                    # If we've been waiting for longer than our timeout then
                    # we'll just continue on in our loop. This provides a
                    # chance for the while loop to be reevaluated.
                    continue

                # Now that we have a request, we'll want to dispatch to our
                # underlying callbacks.
                status, resp_headers, body = (
                    yield from self._callback(*request.as_params())
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
                    yield from self._writer.drain()
        finally:
            writer.close()


class HTTPServer:

    protocol_class = HTTPProtocol

    def __init__(self, callback, loop=None):
        self.callback = callback
        self.loop = None

    def __call__(self):
        return self.protocol_class(self.callback, loop=self.loop)
