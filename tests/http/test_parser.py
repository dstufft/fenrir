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

import pytest

from fenrir.http.parser import HTTPParser


class TestHTTPParser:

    def test_body_length(self):
        parser = HTTPParser()
        parser._content_length = b"15"
        parser.headers_complete = True

        assert parser.body_length == 15

    @pytest.mark.parametrize(
        "length",
        [
            b"abc",
            b"-15",
            b"\xe2\x98\x83",
        ],
    )
    def test_body_length_invalid(self, length):
        parser = HTTPParser()
        parser._content_length = length
        parser.headers_complete = True

        assert parser.body_length == 0

    def test_body_length_defaults_zero(self):
        parser = HTTPParser()
        parser.headers_complete = True

        assert parser.body_length == 0

    def test_basic_parses(self):
        parser = HTTPParser()

        assert parser.execute(b"GET /foo/bar/?q=what HTTP/1.1\r\n") == 31
        assert parser.execute(b"Host: example.com\r\n") == 19
        assert parser.execute(b"Content-Length: 10\r\n") == 20
        assert parser.execute(b"\r\n") == 2
        assert parser.execute(b"01234567zz", 8) == 8
        assert parser.execute(b"89") == 2
        assert parser.execute(b"zzz") == 0

        assert parser.method == b"GET"
        assert parser.path == b"/foo/bar/"
        assert parser.query == b"q=what"
        assert parser.http_version == b"HTTP/1.1"
        assert parser.headers == {
            b"Host": [b"example.com"],
            b"Content-Length": [b"10"],
        }
        assert parser.recv_body() == b"0123456789"

    def test_parser_multiple_invalid_content_length_is_zero(self):
        parser = HTTPParser()
        parser.execute(b"GET /foo/bar/?q=what HTTP/1.1\r\n")
        parser.execute(b"Host: example.com\r\n")
        parser.execute(b"Content-Length: 10\r\n")
        parser.execute(b"Content-Length: 12\r\n")
        parser.execute(b"\r\n")

        assert parser.body_length == 0

    def test_parser_completed(self):
        parser = HTTPParser()
        parser.execute(
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"\r\n"
        )

        assert parser.completed

    @pytest.mark.parametrize(
        "data",
        [
            # Test that we're not completed if we haven't gotten any headers
            b"GET / HTTP/1.1\r\n",

            # Test that if we haven't gotten any of the body that we're not
            # completed
            (
                b"GET / HTTP/1.1\r\n"
                b"Host: example.com\r\n"
                b"Content-Length: 10\r\n"
                b"\r\n"
            ),

            # Test that if we have gotten the body, but not the entire thing
            # that we're not completed
            (
                b"GET / HTTP/1.1\r\n"
                b"Host: example.com\r\n"
                b"Content-Length: 10\r\n"
                b"\r\n"
                b"12345"
            ),
        ],
    )
    def test_parser_not_completed(self, data):
        parser = HTTPParser()
        parser.execute(data)

        assert not parser.completed

    def test_recv_returns_unrecvd_data(self):
        parser = HTTPParser()
        parser.execute(b"GET /foo/bar/?q=what HTTP/1.1\r\n")
        parser.execute(b"Host: example.com\r\n")
        parser.execute(b"Content-Length: 10\r\n")
        parser.execute(b"\r\n")
        parser.execute(b"01234567")

        assert parser.recv_body() == b"01234567"

        parser.execute(b"89")

        assert parser.recv_body() == b"89"
