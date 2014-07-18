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
from fenrir.http.request import Headers, Request


class FakeStreamReader:

    def __init__(self):
        self.data = []
        self.eof = False

    def feed_data(self, data):
        self.data.append(data)

    def feed_eof(self):
        self.eof = True


class TestHeaders:

    def test_init_only_allows_bytes(self):
        with pytest.raises(TypeError):
            Headers([("str", None)])

    def test_only_allows_bytes_keys(self):
        h = Headers([])

        with pytest.raises(TypeError):
            h["Invalid Key"]

    def test_repr(self):
        r = repr(Headers([(b"Content-Length", b"100")]))
        assert r == "Headers({})".format([(b"Content-Length", b"100")])

    def test_iter(self):
        h = Headers([(b"Content-Length", b"100"), (b"Host", b"example.com")])
        assert set(h) == {b"Content-Length", b"Host"}

    def test_len(self):
        h = Headers([(b"Content-Length", b"100"), (b"Host", b"example.com")])
        assert len(h) == 2

    def test_case_insensitive(self):
        assert b"content-length" in Headers([(b"Content-Length", b"100")])


class TestRequest:

    def test_passes_validation(self):
        body = pretend.stub()
        request = Request(
            b"HTTP/1.1", b"GET", b"/", b"q=wat",
            [(b"Host", b"example.com"), (b"Content-Length", b"0")],
            body,
        )

        assert request.http_version == b"HTTP/1.1"
        assert request.method == b"GET"
        assert request.path == b"/"
        assert request.query == b"q=wat"
        assert request.headers == Headers([
            (b"Host", b"example.com"),
            (b"Content-Length", b"0"),
        ])
        assert request.body is body

    @pytest.mark.parametrize(
        "content_lengths",
        [
            [b"-1"],
            [b"\xe2\x98\x83"],
            [b"0", b"1"],
        ],
    )
    def test_invalid_content_length(self, content_lengths):
        with pytest.raises(BadRequest):
            Request(
                b"HTTP/1.1", b"GET", b"/", b"q=wat",
                [(b"Host", b"example.com")]
                +
                [(b"Content-Length", cl) for cl in content_lengths],
                None,
            )

    @pytest.mark.parametrize(
        "hosts",
        [
            [],
            [b"example.com", b"foo.example.com"],
        ],
    )
    def test_invalid_hosts(self, hosts):
        with pytest.raises(BadRequest):
            Request(
                b"HTTP/1.1", b"GET", b"/", b"q=wat",
                [(b"Host", h) for h in hosts],
                None,
            )

    def test_params(self):
        request = Request(
            b"HTTP/1.1", b"GET", b"/", b"q=wat",
            [(b"Host", b"example.com"), (b"Content-Length", b"0")],
            None,
        )

        assert request.as_params() == (request, request.body)
