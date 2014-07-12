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
import pytest

from fenrir import server


class TestServer:

    def test_app_resolves(self, monkeypatch):
        app = pretend.stub()
        resolve_app = pretend.call_recorder(lambda appn: app)
        monkeypatch.setattr(server, "resolve_app", resolve_app)

        s = server.Server("example:test")

        assert s.app is app
        assert resolve_app.calls == [pretend.call("example:test")]

    def test_passing_in_app(self):
        app = pretend.stub()
        s = server.Server(app)

        assert s.app is app

    @pytest.mark.parametrize(
        ("bind", "expected"),
        [
            (None, [("localhost", 8000)]),
            (["0.0.0.0"], [("0.0.0.0", 8000)]),
            (["0.0.0.0:9000"], [("0.0.0.0", 9000)]),
            (["thing.example.com:5000"], [("thing.example.com", 5000)]),
            (["thing.example.com"], [("thing.example.com", 8000)]),
            (["[::1]:7500"], [("::1", 7500)]),
            (["[::1]"], [("::1", 8000)]),
            (
                ["127.0.0.1", "127.0.0.2:9000"],
                [("127.0.0.1", 8000), ("127.0.0.2", 9000)],
            ),
        ],
    )
    def test_bind(self, bind, expected):
        s = server.Server(pretend.stub(), bind=bind)
        assert s.bind == expected

    def test_spawn(self, monkeypatch):
        result = pretend.stub()
        server_obj = pretend.stub(
            wait_closed=pretend.call_recorder(lambda: result),
        )
        loop = pretend.stub(
            run_until_complete=pretend.call_recorder(lambda coro: coro),
            create_server=pretend.call_recorder(
                lambda factory, **kw: server_obj
            ),
        )
        get_event_loop = pretend.call_recorder(lambda: loop)
        wait_coro = pretend.stub()
        wait = pretend.call_recorder(lambda coros: wait_coro)

        httpserver_obj = pretend.call()
        httpserver_cls = pretend.call_recorder(
            lambda app, **kw: httpserver_obj
        )

        monkeypatch.setattr(asyncio, "get_event_loop", get_event_loop)
        monkeypatch.setattr(asyncio, "wait", wait)
        monkeypatch.setattr(server, "HTTPServer", httpserver_cls)

        app = pretend.stub()
        s = server.Server(app, bind=["127.0.0.1:4000", "0.0.0.0"])
        s.spawn()

        assert get_event_loop.calls == [pretend.call()]
        assert httpserver_cls.calls == [
            pretend.call(app, loop=loop),
            pretend.call(app, loop=loop),
        ]
        assert loop.create_server.calls == [
            pretend.call(httpserver_obj, host="127.0.0.1", port=4000),
            pretend.call(httpserver_obj, host="0.0.0.0", port=8000),
        ]
        assert loop.run_until_complete.calls == [
            pretend.call(server_obj),
            pretend.call(server_obj),
            pretend.call(wait_coro),
        ]
        assert server_obj.wait_closed.calls == [pretend.call(), pretend.call()]
        assert wait.calls == [pretend.call([result, result])]
