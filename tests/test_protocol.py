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

import pretend

from fenrir.http.errors import HTTPError, BadRequest
from fenrir.http.req import Request
from fenrir.protocol import HTTPProtocol, HTTPServer
from fenrir.queues import CloseableQueue


def sync(coro):
    if asyncio.iscoroutine(coro):
        try:
            next(coro)
        except StopIteration as exc:
            return exc.value
    else:
        return coro


class StringTransport(asyncio.Transport):
    pass


class FakeStreamReader:

    def __init__(self, loop=None):
        self._eof = False
        self._buffer = bytearray()
        self._loop = loop

    def at_eof(self):
        return not self._buffer and self._eof

    def feed_data(self, data):
        assert not self._eof
        self._buffer.extend(data)

    def feed_eof(self):
        self._eof = True

    @asyncio.coroutine
    def read(self, size=None):
        if size is None:
            data = self._buffer[:]
            self._buffer = bytearray()
        else:
            data = self._buffer[:size]
            self._buffer = self._buffer[size:]

        return bytes(data)


class FakeStreamWriter:

    def __init__(self):
        self.buffer = bytearray()
        self.drained = bytearray()
        self.closed = False

    def write(self, data):
        assert not self.closed
        self.buffer.extend(data)

    @asyncio.coroutine
    def drain(self):
        assert not self.closed
        self.drained.extend(self.buffer)
        self.buffer = bytearray()

    def close(self):
        self.closed = True


class TestHTTPProtocol:

    def test_initialization(self):
        app = pretend.stub()
        protocol = HTTPProtocol(app)

        assert protocol.writer is None
        assert protocol.reader is None
        assert protocol.app is app

    def test_connection_made(self, monkeypatch):
        app = pretend.stub()
        loop = pretend.stub()
        protocol = HTTPProtocol(app, loop=loop)
        transport = StringTransport()

        async = pretend.call_recorder(lambda coro, loop: None)

        # Prevent from calling asyncio.async which will trigger the event loop
        monkeypatch.setattr(asyncio, "async", async)

        # Override our process_data and process_responses so that we can ensure
        # they've been called.
        process_data_coro = pretend.stub()
        protocol.process_data = pretend.call_recorder(
            lambda reader, requests: process_data_coro
        )
        process_responses_coro = pretend.stub()
        protocol.process_responses = pretend.call_recorder(
            lambda writer, requests: process_responses_coro
        )

        # Simulate a fake connection with our StringTransport
        protocol.connection_made(transport)

        # Ensure that we've created a reader and writer for this connection
        assert isinstance(protocol.reader, asyncio.StreamReader)
        assert isinstance(protocol.writer, asyncio.StreamWriter)

        # Make sure that our reader is participating in flow control and has
        # been given our transport
        assert protocol.reader._transport is transport

        # Ensure that we've started up a coroutine for our producer and
        # consumer.
        assert len(protocol.process_data.calls) == 1
        assert len(protocol.process_data.calls[0].args) == 2
        assert not protocol.process_data.calls[0].kwargs
        assert isinstance(
            protocol.process_data.calls[0].args[0],
            asyncio.StreamReader,
        )
        assert isinstance(
            protocol.process_data.calls[0].args[1],
            CloseableQueue,
        )

        assert len(protocol.process_responses.calls) == 1
        assert len(protocol.process_responses.calls[0].args) == 2
        assert not protocol.process_responses.calls[0].kwargs
        assert isinstance(
            protocol.process_responses.calls[0].args[0],
            asyncio.StreamWriter,
        )
        assert isinstance(
            protocol.process_responses.calls[0].args[1],
            CloseableQueue,
        )

        assert async.calls == [
            pretend.call(process_data_coro, loop=loop),
            pretend.call(process_responses_coro, loop=loop),
        ]

    def test_connection_lost_no_exc(self):
        app = pretend.stub()
        loop = pretend.stub()
        protocol = HTTPProtocol(app, loop=loop)
        protocol.reader = pretend.stub(
            feed_eof=pretend.call_recorder(lambda: None),
        )

        protocol.connection_lost(None)

        assert protocol.reader.feed_eof.calls == [pretend.call()]

    def test_connection_lost_with_exc(self):
        app = pretend.stub()
        loop = pretend.stub()
        protocol = HTTPProtocol(app, loop=loop)
        protocol.reader = pretend.stub(
            set_exception=pretend.call_recorder(lambda exc: None),
        )

        exc = pretend.stub()
        protocol.connection_lost(exc)

        assert protocol.reader.set_exception.calls == [pretend.call(exc)]

    def test_data_received_feeds_reader(self):
        app = pretend.stub()
        loop = pretend.stub()
        protocol = HTTPProtocol(app, loop=loop)
        protocol.reader = pretend.stub(
            feed_data=pretend.call_recorder(lambda data: None),
        )

        data = b"This is some Fake Data"
        protocol.data_received(data)

        assert protocol.reader.feed_data.calls == [pretend.call(data)]

    def test_eof_received_feeds_reader(self):
        app = pretend.stub()
        loop = pretend.stub()
        protocol = HTTPProtocol(app, loop=loop)
        protocol.reader = pretend.stub(
            feed_eof=pretend.call_recorder(lambda: None),
        )

        protocol.eof_received()

        assert protocol.reader.feed_eof.calls == [pretend.call()]

    def test_process_data(self, monkeypatch):
        monkeypatch.setattr(asyncio, "StreamReader", FakeStreamReader)

        reader = FakeStreamReader()
        requests = CloseableQueue(loop=pretend.stub())

        reader.feed_data(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"\r\n"
        )
        reader.feed_eof()

        protocol = HTTPProtocol(pretend.stub(), loop=pretend.stub())

        assert not reader.at_eof()
        assert not requests.closed

        sync(protocol.process_data(reader, requests))

        assert reader.at_eof()
        assert requests.closed
        assert requests.qsize() == 1

        request = requests.get_nowait()

        assert isinstance(request, Request)

    def test_process_data_bad_request(self, monkeypatch):
        monkeypatch.setattr(asyncio, "StreamReader", FakeStreamReader)

        reader = FakeStreamReader()
        requests = CloseableQueue(loop=pretend.stub())

        reader.feed_data(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Content-Length: invalid\r\n"
            b"\r\n"
        )
        reader.feed_eof()

        protocol = HTTPProtocol(pretend.stub(), loop=pretend.stub())

        assert not reader.at_eof()
        assert not requests.closed

        sync(protocol.process_data(reader, requests))

        assert reader.at_eof()
        assert requests.closed
        assert requests.qsize() == 1

        request = requests.get_nowait()

        assert isinstance(request, BadRequest)

    def test_process_data_multiple_requests(self, monkeypatch):
        monkeypatch.setattr(asyncio, "StreamReader", FakeStreamReader)

        reader = FakeStreamReader()
        requests = CloseableQueue(loop=pretend.stub())

        reader.feed_data(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
        )
        reader.feed_eof()

        protocol = HTTPProtocol(pretend.stub(), loop=pretend.stub())

        assert not reader.at_eof()
        assert not requests.closed

        sync(protocol.process_data(reader, requests))

        assert reader.at_eof()
        assert requests.closed
        assert requests.qsize() == 2

        assert all(
            isinstance(requests.get_nowait(), Request)
            for r in range(requests.qsize())
        )

    def test_process_data_http10_implicit_close(self, monkeypatch):
        monkeypatch.setattr(asyncio, "StreamReader", FakeStreamReader)

        reader = FakeStreamReader()
        requests = CloseableQueue(loop=pretend.stub())

        reader.feed_data(
            b"GET / HTTP/1.0\r\n"
            b"Host: example.com\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
            b"GET / HTTP/1.0\r\n"
            b"Host: example.com\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
        )
        reader.feed_eof()

        protocol = HTTPProtocol(pretend.stub(), loop=pretend.stub())

        assert not reader.at_eof()
        assert not requests.closed

        sync(protocol.process_data(reader, requests))

        assert reader.at_eof()
        assert requests.closed
        assert requests.qsize() == 1

        request = requests.get_nowait()

        assert isinstance(request, Request)

    def test_process_data_http11_connection_close(self, monkeypatch):
        monkeypatch.setattr(asyncio, "StreamReader", FakeStreamReader)

        reader = FakeStreamReader()
        requests = CloseableQueue(loop=pretend.stub())

        reader.feed_data(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Content-Length: 0\r\n"
            b"Connection: close\r\n"
            b"\r\n"
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
        )
        reader.feed_eof()

        protocol = HTTPProtocol(pretend.stub(), loop=pretend.stub())

        assert not reader.at_eof()
        assert not requests.closed

        sync(protocol.process_data(reader, requests))

        assert reader.at_eof()
        assert requests.closed
        assert requests.qsize() == 1

        request = requests.get_nowait()

        assert isinstance(request, Request)

    def test_process_data_larger_one_read(self, monkeypatch):
        monkeypatch.setattr(asyncio, "StreamReader", FakeStreamReader)

        reader = FakeStreamReader()
        requests = CloseableQueue(loop=pretend.stub())

        reader.feed_data(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Content-Length: 8192\r\n"
            b"Connection: close\r\n"
            b"\r\n"
        )
        reader.feed_data(b"0" * 8192)
        reader.feed_eof()

        protocol = HTTPProtocol(pretend.stub(), loop=pretend.stub())

        assert not reader.at_eof()
        assert not requests.closed

        sync(protocol.process_data(reader, requests))

        assert reader.at_eof()
        assert requests.closed
        assert requests.qsize() == 1

        request = requests.get_nowait()

        assert isinstance(request, Request)

    def test_process_responses(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request = Request(FakeStreamReader())
        request.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (b"200 OK", {}, [])
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
        )

    def test_process_responses_queue_timeout_retries(self, monkeypatch):
        class WaitFor:
            def __init__(self, num):
                self.num = num
                self.called = 0

            def __call__(self, coro, *a, **kw):
                self.called += 1
                if self.called < self.num:
                    raise asyncio.TimeoutError
                return coro

        wait_for = WaitFor(2)
        monkeypatch.setattr(asyncio, "wait_for", wait_for)

        request = Request(FakeStreamReader())
        request.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (b"200 OK", {}, [])
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert wait_for.called == 2
        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
        )

    def test_process_responses_http_error(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request = HTTPError()
        request.as_response = lambda: (b"400 Bad Request", {}, [b"Foo Bar"])

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (b"200 OK", {}, [])
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained)[:110] == (
            b"HTTP/1.1 400 Bad Request\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 7\r\n"
            b"\r\n"
            b"Foo Bar"
        )

    def test_process_responses_accepts_headers(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request = Request(FakeStreamReader())
        request.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (b"200 OK", {b"Test": b"Yes!"}, [])
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 0\r\n"
            b"Test: Yes!\r\n"
            b"\r\n"
        )

    def test_process_responses_accepts_header_list(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request = Request(FakeStreamReader())
        request.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (b"200 OK", {b"Test": [b"Yes!", b"No!"]}, [])
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 0\r\n"
            b"Test: Yes!,No!\r\n"
            b"\r\n"
        )

    def test_process_responses_accepts_header_list_cookie(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request = Request(FakeStreamReader())
        request.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (
                b"200 OK",
                {b"Set-Cookie": [b"One=Win", b"Two=Wat"]},
                [],
            )
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 0\r\n"
            b"Set-Cookie: One=Win\r\n"
            b"Set-Cookie: Two=Wat\r\n"
            b"\r\n"
        )

    def test_process_responses_explicit_content_length(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request = Request(FakeStreamReader())
        request.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (
                b"200 OK",
                {b"Content-Length": b"10"},
                [b"12345", b"6789", b"0zzz", b"yyyy"],
            )
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 10\r\n"
            b"\r\n"
            b"1234567890"
        )

    def test_process_responses_single_coroutine(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request = Request(FakeStreamReader())
        request.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (
                b"200 OK",
                {},
                [asyncio.coroutine(lambda: b"abcdefgh")()],
            )
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 8\r\n"
            b"\r\n"
            b"abcdefgh"
        )

    def test_process_responses_has_coroutines(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request = Request(FakeStreamReader())
        request.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (
                b"200 OK",
                {},
                [
                    asyncio.coroutine(lambda: b"abcdefgh")(),
                    asyncio.coroutine(lambda: b"abcdefgh")(),
                ],
            )
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        sync(protocol.process_responses(writer, requests))

        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"\r\n"
            b"abcdefghabcdefgh"
        )

    def test_process_responses_throws_away_pending(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request_1 = Request(FakeStreamReader())
        request_1.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        request_2 = Request(FakeStreamReader())
        request_2.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request_1)
        requests.put_nowait(request_2)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (b"200 OK", {}, [b"abcde", b"fgh"])
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        assert requests.qsize() == 2

        sync(protocol.process_responses(writer, requests))

        assert requests.qsize() == 0
        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"\r\n"
            b"abcdefgh"
        )

    def test_process_responses_multiple_correct_order(self, monkeypatch):
        monkeypatch.setattr(asyncio, "wait_for", lambda coro, *a, **kw: coro)

        request_1 = Request(FakeStreamReader())
        request_1.add_bytes(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        request_2 = Request(FakeStreamReader())
        request_2.add_bytes(
            b"GET /foo/bar/ HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Connection-Length: 0\r\n"
            b"\r\n"
        )

        writer = FakeStreamWriter()
        requests = CloseableQueue()
        requests.put_nowait(request_1)
        requests.put_nowait(request_2)
        requests.close()

        app = asyncio.coroutine(
            lambda req, body: (b"200 OK", {b"URL": req.path}, [b"abcdefgh"])
        )

        protocol = HTTPProtocol(app, loop=pretend.stub())

        assert requests.qsize() == 2

        sync(protocol.process_responses(writer, requests))

        assert requests.qsize() == 0
        assert writer.closed
        assert not writer.buffer
        assert bytes(writer.drained) == (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Length: 8\r\n"
            b"URL: /\r\n"
            b"\r\n"
            b"abcdefgh"
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n"
            b"Content-Length: 8\r\n"
            b"URL: /foo/bar/\r\n"
            b"\r\n"
            b"abcdefgh"
        )


class TestHTTPServer:

    def test_basic_factory(self):
        protocol_instance = pretend.stub()
        protocol = pretend.call_recorder(lambda cb, loop: protocol_instance)
        app = pretend.stub()

        factory = HTTPServer(app)
        factory.protocol_class = protocol

        assert factory() is protocol_instance
        assert factory.protocol_class.calls == [
            pretend.call(app, loop=None),
        ]
