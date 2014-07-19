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

from fenrir.c import http11


class ParserError(Exception):
    """
    Raised when there is an error parsing the HTTP message.
    """


class HTTPParser:
    """
    A small wrapper around the CFFI bindings for the HTTP/1.1 parser that was
    pulled from Mongrel2.
    """

    def __init__(self):
        # Create a http_parser struct so to act as a bag of data to store
        # information about what we're parsing into
        self._parser = http11.ffi.new("http_parser *")

        # Initialize our http_parser struct
        http11.lib.http_parser_init(self._parser)

        # Create our callback functions, these are FFI callback instances which
        # we store on our instance because if we allow them to get garbage
        # collected before they're called by the C code then when they get
        # called the process will segfault.
        self._cb_http_version = http11.element_cb(self._cb_http_version)
        self._cb_request_method = http11.element_cb(self._cb_request_method)
        self._cb_request_path = http11.element_cb(self._cb_request_path)
        self._cb_query_string = http11.element_cb(self._cb_query_string)
        self._cb_http_field = http11.field_cb(self._cb_http_field)

        # Actually register our callbacks with our http_parser instance
        self._parser.http_version = self._cb_http_version
        self._parser.request_method = self._cb_request_method
        self._parser.request_path = self._cb_request_path
        self._parser.query_string = self._cb_query_string
        self._parser.http_field = self._cb_http_field

        # Keep track of our high water mark of bytes parsed
        self._parsed = 0

        # Keep track of our state
        self.http_version = None
        self.method = None
        self.path = None
        self.query = None
        self.headers = []
        self.finished = False

    def _cb_http_version(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == http11.ffi.NULL

        self.http_version = http11.ffi.buffer(at, length)[:]

    def _cb_request_method(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == http11.ffi.NULL

        self.method = http11.ffi.buffer(at, length)[:]

    def _cb_request_path(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == http11.ffi.NULL

        self.path = http11.ffi.buffer(at, length)[:]

    def _cb_query_string(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == http11.ffi.NULL

        self.query = http11.ffi.buffer(at, length)[:]

    def _cb_http_field(self, data, field, flen, value, vlen):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == http11.ffi.NULL

        # We need to get the field name and the value from our buffers so that
        # we can use that data as our headers.
        field = http11.ffi.buffer(field, flen)[:]
        value = http11.ffi.buffer(value, vlen)[:].strip()

        # Actually add the parsed value to our stored headers
        self.headers.append((field, value))

    def parse(self, data, length=None, offset=0):
        # If we were not given a length, then we assume we're to parse the
        # entire length of the data minus the offset
        if length is None:
            length = len(data) - offset

        # Quick sanity check to ensure that our length and offset together are
        # not greater than the length of the data we have.
        if offset + length > len(data):
            raise ValueError("Cannot read more data than exists.")

        # Actually parse the chunk of data we've been given. The return value
        # will be how much data was actually parsed.
        parsed = http11.lib.http_parser_execute(
            self._parser,
            data,
            # We add the offset to the length here because the C parser wants
            # the total length it should read including the offset. However I
            # think slice syntax is nicer so HTTPParser().parse() wants similar
            # numbers and this will translate it.
            length + offset,
            offset,
        )

        # The mongrel2 HTTP/1.1 parser returns the total number of bytes
        # parsed. We want to only include the amount parsed *this* time so we
        # keep track of how much we've parsed and subtract it.
        parsed -= self._parsed
        self._parsed += parsed

        # Ensure that there was not an error during the parsing of the last
        # chunk of data.
        parser_state = http11.lib.http_parser_finish(self._parser)
        assert parser_state in http11.PARSER_STATES
        if parser_state == http11.PARSER_ERROR:
            raise ParserError(data[offset:length])
        elif parser_state == http11.PARSER_COMPLETE:
            self.finished = True

        return parsed
