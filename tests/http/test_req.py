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

import pretend
import pytest

from fenrir.http.req import Request


class FakeParser:

    def __init__(self, received_at=None):
        self.data = []
        self.body = []
        self.headers_complete = False
        self.has_body = False
        self.completed = False
        self.max_data = 0
        self.received_at = received_at

    def execute(self, data):
        self.max_data += 1

        if self.headers_complete:
            self.body.append(data)

            if (self.received_at is not None
                    and self.max_data >= self.received_at):
                self.completed = True
        else:
            self.data.append(data)

    def recv_body(self):
        data = b"".join(self.body)
        self.body = []
        return data


class FakeStreamReader:

    def __init__(self):
        self.data = []
        self.eof = False

    def feed_data(self, data):
        self.data.append(data)

    def feed_eof(self):
        self.eof = True


class TestRequest:

    def test_request_body(self):
        body = pretend.stub()
        assert Request(body).body is body

    @pytest.mark.parametrize(
        ("attribute", "passthrough"),
        [
            ("http_version", ...),
            ("method", ...),
            ("path", ...),
            ("query", ...),
            ("headers", ...),
            ("headers_complete", ...),
            ("received", "completed"),
        ],
    )
    def test_request_passthrough(self, attribute, passthrough):
        if passthrough is Ellipsis:
            passthrough = attribute

        value = pretend.stub()
        req = Request(None)
        req._parser = pretend.stub(**{passthrough: value})

        assert getattr(req, attribute) is value

    def test_request_add_bytes_empty_no_ops(self):
        req = Request(None)
        req._parser = pretend.stub(
            execute=pretend.call_recorder(lambda d: None),
        )

        req.add_bytes(b"")
        assert req._parser.execute.calls == []

    def test_request_add_bytes_executes_parser(self):
        req = Request(FakeStreamReader())
        req._parser = FakeParser(received_at=5)

        req.add_bytes(b"abc")
        req.add_bytes(b"zdefgh")

        assert req._parser.data == [b"abc", b"zdefgh"]

        req._parser.headers_complete = True
        req._parser.has_body = True

        req.add_bytes(b"123")
        req.add_bytes(b"456")

        assert req.body.data == [b"123", b"456"]
        assert not req.body.eof

        req.add_bytes(b"789")

        assert req.body.data == [b"123", b"456", b"789"]
        assert req.body.eof

    def test_request_add_bytes_extends_body_after_headers(self):
        req = Request(None)
        req._parser = FakeParser()

    def test_request_as_params(self):
        body = pretend.stub()
        req = Request(body)

        assert req.as_params() == (req, body)
