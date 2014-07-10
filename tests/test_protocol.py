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

from fenrir.protocol import HTTPProtocol, HTTPServer
from fenrir.queues import CloseableQueue


class StringTransport(asyncio.Transport):
    pass


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
