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

from fenrir.http.errors import BadRequest
from fenrir.http.req import Headers, Request, _header_parse, _header_join


class FakeParser:

    def __init__(self, received_at=None):
        self.data = []
        self.body = []
        self.headers = {}
        self.headers_complete = False
        self.body_length = 0
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


class TestHeaders:

    @pytest.mark.parametrize(
        ("value", "delim", "expected"),
        [
            (b"foo", None, b"foo"),
            (b"foo,bar", None, b'"foo,bar"'),
            (b'foo,bar"win', None, b'"foo,bar\\"win"'),
            (b"foo", b";", b"foo"),
            (b"foo;bar", b";", b'"foo;bar"'),
            (b'foo;bar"win', b";", b'"foo;bar\\"win"'),
        ],
    )
    def test_header_parse(self, value, delim, expected):
        if delim is not None:
            args = [value, delim]
        else:
            args = [value]

        assert _header_parse(*args) == expected

    @pytest.mark.parametrize(
        ("header", "values", "expected"),
        [
            (b"Foo", [b"One", b"Two"], b"One,Two"),
            (b"Cookie", [b"One=Wat", b"Two=Ok"], b"One=Wat; Two=Ok"),
        ],
    )
    def test_header_join(self, header, values, expected):
        assert _header_join(header, values) == expected

    def test_init_only_allows_bytes(self):
        with pytest.raises(TypeError):
            Headers({"str": None})

    def test_only_allows_bytes_keys(self):
        h = Headers({})

        with pytest.raises(TypeError):
            h["Invalid Key"]

    def test_repr(self):
        r = repr(Headers({b"Content-Length": [b"100"]}))
        assert r == "<Headers {}>".format({b"Content-Length": b"100"})

    def test_iter(self):
        h = Headers({b"Content-Length": [b"100"], b"Host": [b"example.com"]})
        assert set(h) == {b"Content-Length", b"Host"}

    def test_len(self):
        h = Headers({b"Content-Length": [b"100"], b"Host": [b"example.com"]})
        assert len(h) == 2


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

        req._parser.headers[b"Host"] = [b"example.com"]
        req._parser.headers_complete = True
        req._parser.body_length = 9

        req.add_bytes(b"123")
        req.add_bytes(b"456")

        assert req.body.data == [b"123", b"456"]
        assert not req.body.eof

        req.add_bytes(b"789")

        assert req.body.data == [b"123", b"456", b"789"]
        assert req.body.eof

    def test_request_add_bytes_empty_body(self):
        req = Request(FakeStreamReader())
        req._parser = FakeParser(received_at=1)
        req._parser.headers_complete = True
        req._parser.headers[b"Host"] = [b"example.com"]
        req._parser.body_length = 0

        req.add_bytes(b"123")

        assert req.body.data == []
        assert req.body.eof

    def test_request_validates(self):
        req = Request(FakeStreamReader())
        req._parser = FakeParser(received_at=1)
        req._parser.headers_complete = True
        req._parser.headers[b"Host"] = [b"example.com"]
        req._parser.body_length = 3

        req.add_bytes(b"123")

        assert req._validated

    def test_request_as_params(self):
        body = pretend.stub()
        req = Request(body)

        assert req.as_params() == (req, body)


class TestRequestValidation:

    def test_succeeds(self):
        req = Request(FakeStreamReader())
        req._parser = FakeParser()
        req._parser.headers_complete = True
        req._parser.headers[b"Host"] = [b"example.com"]

        req.validate()

        assert req._validated

    @pytest.mark.parametrize(
        "content_length",
        [
            [b"-1"],
            [b"\xe2\x98\x83"],
        ],
    )
    def test_fails_invalid_content_length(self, content_length):
        req = Request(FakeStreamReader())
        req._parser = FakeParser()
        req._parser.headers_complete = True
        req._parser.headers[b"Content-Length"] = content_length
        req._parser.headers[b"Host"] = [b"example.com"]

        with pytest.raises(BadRequest):
            req.validate()

    def test_fails_no_host(self):
        req = Request(FakeStreamReader())
        req._parser = FakeParser()
        req._parser.headers_complete = True

        with pytest.raises(BadRequest):
            req.validate()
