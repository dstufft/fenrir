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

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser


class HTTPProtocol(FlowControlMixin, asyncio.Protocol):

    def __init__(self, stream_reader, callback, loop=None):
        super().__init__(loop=loop)
        self._stream_reader = stream_reader
        self._stream_writer = None

        self._callback = callback

        self._headers_parsed = False

    def connection_made(self, transport):
        self._parser = HttpParser()

        self._stream_reader.set_transport(transport)
        self._stream_writer = asyncio.StreamWriter(
            transport,
            self,
            self._stream_reader,
            self._loop,
        )

    def connection_lost(self, exc):
        if exc is None:
            self._stream_reader.feed_eof()
        else:
            self._stream_reader.set_exception(exc)

        super().connection_lost(exc)

    def data_received(self, data):
        # Parse our incoming data with our HTTP parser
        self._parser.execute(data, len(data))

        # If we have not already handled the headers and we've gotten all of
        # them, then invoke the callback with the headers in them.
        if not self._headers_parsed and self._parser.is_headers_complete():
            self._headers_parsed = True
            coro = self.dispatch(
                self._parser.get_headers(),
                self._stream_reader,
                self._stream_writer,
            )
            asyncio.Task(coro, loop=self._loop)

        # Determine if we have any data in the body buffer and if so feed it
        # to our StreamReader
        if self._parser.is_partial_body():
            d = self._parser.recv_body()
            # self._stream_reader.feed_data(self._parser.recv_body())
            self._stream_reader.feed_data(d)

        # Determine if we've completed the end of the HTTP request, if we have
        # then we should close our stream reader because there is nothing more
        # to read.
        if self._parser.is_message_complete():
            self._stream_reader.feed_eof()

    def eof_received(self):
        # We've gotten an EOF from the client, so we'll propagate this to our
        # StreamReader
        self._stream_reader.feed_eof()

    @asyncio.coroutine
    def dispatch(self, headers, reader, writer):
        # Get the status, headers, and body from the callback. The body must
        # be iterable, and each item can either be a bytes object, or an
        # asyncio coroutine, in which case we'll ``yield from`` on it to wait
        # for it's value.
        status, resp_headers, body = yield from self._callback(headers, reader)

        # Write out the status line to the client for this request
        # TODO: We probably don't want to hard code HTTP/1.1 here
        writer.write(b"HTTP/1.1 " + status + b"\r\n")

        # Write out the headers, taking special care to ensure that any
        # mandatory headers are added.
        # TODO: How do we handle multi value headers like Set-Cookie?
        # TODO: We need to handle some required headers
        for key, value in resp_headers.items():
            writer.write(key + b": " + value + b"\r\n")

        # Before we get to the body, we need to write a blank line to separate
        # the headers and the response body
        writer.write(b"\r\n")

        for chunk in body:
            # If the chunk is a coroutine, then we want to wait for the result
            # before we write it.
            if asyncio.iscoroutine(chunk):
                chunk = yield from chunk

            # Write our chunk out to the connect client
            writer.write(chunk)

        # We've written everything in our iterator, so we want to close the
        # connection.
        writer.close()


class HTTPServer:

    protocol_class = HTTPProtocol

    def __init__(self, callback, loop=None):
        self.callback = callback
        self.loop = None

    def __call__(self):
        reader = asyncio.StreamReader(loop=self.loop)
        protocol = self.protocol_class(reader, self.callback, loop=self.loop)
        return protocol
