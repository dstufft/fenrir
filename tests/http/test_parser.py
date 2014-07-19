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

import collections

import pytest

from fenrir.http.parser import HTTPParser, ParserError


ParserResult = collections.namedtuple(
    "ParserResult",
    ["http_version", "method", "path", "query", "headers"],
)


class TestHTTPParser:

    @pytest.mark.parametrize(
        ("lines", "expected"),
        [
            (
                [b"GET / HTTP/1.1\r\n", b"\r\n"],
                ParserResult(b"HTTP/1.1", b"GET", b"/", None, []),
            ),
            (
                [b"GET /?q=wat HTTP/1.1\r\n", b"\r\n"],
                ParserResult(b"HTTP/1.1", b"GET", b"/", b"q=wat", []),
            ),
            (
                [b"GET / HTTP/1.1\r\n", b"Foo: Bar\r\n", b"\r\n"],
                ParserResult(
                    b"HTTP/1.1",
                    b"GET",
                    b"/",
                    None,
                    [(b"Foo", b"Bar")],
                ),
            ),
            (
                [
                    b"GET / HTTP/1.1\r\n",
                    b"Foo: Bar\r\n",
                    b"Wat: Ok\r\n",
                    b"Foo: BarTwo\r\n",
                    b"\r\n",
                ],
                ParserResult(
                    b"HTTP/1.1",
                    b"GET",
                    b"/",
                    None,
                    [(b"Foo", b"Bar"), (b"Wat", b"Ok"), (b"Foo", b"BarTwo")],
                ),
            ),
        ],
    )
    def test_parse_success(self, lines, expected):
        parser = HTTPParser()
        for line in lines:
            assert parser.parse(line) == len(line)

        assert parser.finished
        assert parser.http_version == expected.http_version
        assert parser.method == expected.method
        assert parser.path == expected.path
        assert parser.query == expected.query
        assert parser.headers == expected.headers

    @pytest.mark.parametrize(
        "lines",
        [
            [b"GET / HTTP/1.1\r\n", b"Foo : Bar\r\n"],
        ],
    )
    def test_parse_error(self, lines):
        parser = HTTPParser()
        for line in lines[:-1]:
            assert parser.parse(line) == len(line)

        with pytest.raises(ParserError):
            parser.parse(lines[-1])

    def test_parse_offset_length(self):
        msg = (
            b"GET / HTTP/1.1\r\n"
            b"Foo: Bar\r\n"
            b"\r\n"
        )

        parser = HTTPParser()

        assert parser.parse(msg, 5) == 5
        assert parser.parse(msg, 10, 5) == 10
        assert parser.parse(msg, offset=15) == 13

        assert parser.finished
        assert parser.http_version == b"HTTP/1.1"
        assert parser.method == b"GET"
        assert parser.path == b"/"
        assert parser.query is None
        assert parser.headers == [(b"Foo", b"Bar")]

    def test_parse_past_data_end(self):
        msg = (
            b"GET / HTTP/1.1\r\n"
            b"Foo: Bar\r\n"
            b"\r\n"
        )

        parser = HTTPParser()

        with pytest.raises(ValueError):
            parser.parse(msg, 10000)

    def test_bad_request_improperly_escaped_urls(self):
        """
        RFC 7230 Section 3.1.1 states:

        Recipients of an invalid request-line SHOULD respond with either a 400
        (Bad Request) error or a 301 (Moved Permanently) redirect with the
        request-target properly encoded. A recipient SHOULD NOT attempt to
        autocorrect and then process the request without a redirect, since the
        invalid request-line might be deliberately crafted to bypass security
        filters along the request chain.
        """
        parser = HTTPParser()

        with pytest.raises(ParserError):
            parser.parse(b"GET /foo bar/ HTTP/1.1\r\n\r\n")

    def test_parser_error_space_in_field_name(self):
        """
        RFC 7320 Section 3.2.4 states:

        No whitespace is allowed between the header field-name and colon. In
        the past, differences in the handling of such whitespace have led to
        security vulnerabilities in request routing and response handling. A
        server MUST reject any received request message that contains
        whitespace between a header field-name and colon with a response code
        of 400 (Bad Request).
        """
        parser = HTTPParser()

        with pytest.raises(ParserError):
            parser.parse(b"GET / HTTP/1.1\r\nFoo : Bar\r\n\r\n")
