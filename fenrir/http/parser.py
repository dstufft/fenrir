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

import zero_buffer

from fenrir.http import http11
from fenrir.http.errors import BadRequest


class HTTPParser:

    def __init__(self):
        # Initialize some values which we'll use to store information about
        # what we've parsed so far.
        self.http_version = None
        self.method = None
        self.path = None
        self.query = None
        self.headers = {}  # TODO: We need this to be a different structure
        self.headers_complete = False
        self._buffer = None
        self._buffer_pos = 0

        # Create a http_parser struct so to act as a bag of data to store
        # information about what we're parsing into
        self._parser = http11.ffi.new("http_parser *")

        # Initialize our http_parser struct
        http11.lib.http_parser_init(self._parser)

        # Create our callback functions, these are FFI callback instances which
        # we store on our instance because if we allow them to get garbage
        # collected before they're called by the C code.
        self._cb_header_done = http11.element_cb(self._cb_header_done)
        self._cb_http_version = http11.element_cb(self._cb_http_version)
        self._cb_request_method = http11.element_cb(self._cb_request_method)
        self._cb_request_path = http11.element_cb(self._cb_request_path)
        self._cb_query_string = http11.element_cb(self._cb_query_string)
        self._cb_http_field = http11.field_cb(self._cb_http_field)

        # Actually register our callbacks with our http_parser instance
        self._parser.header_done = self._cb_header_done
        self._parser.http_version = self._cb_http_version
        self._parser.request_method = self._cb_request_method
        self._parser.request_path = self._cb_request_path
        self._parser.query_string = self._cb_query_string
        self._parser.http_field = self._cb_http_field

    @property
    def completed(self):
        return (self.headers_complete
                and (not self.body_length
                     or (self._buffer is not None
                         and self._buffer.writepos >= self._buffer.capacity)))

    @property
    def has_body(self):
        return self._buffer is not None

    @property
    def body_length(self):
        # According to RFC 7230 section 3.3.3 the message body length of a
        # request follows these rules:
        #
        # 1. If a Transfer-Encoding header field is present and the chunked
        #    transfer coding (Section 4.1) is the final encoding, the message
        #    body length is determined by reading and decoding the chunked data
        #    until the transfer coding indicates the data is complete.
        #
        #    If a Transfer-Encoding header field is present in a request and
        #    the chunked transfer coding is not the final encoding, the message
        #    body length cannot be determined reliably; the server MUST respond
        #    with the 400 (Bad Request) status code and then close the
        #    connection.
        #
        #    If a message is received with both a Transfer-Encoding and a
        #    Content-Length header field, the Transfer-Encoding overrides the
        #    Content-Length. Such a message might indicate an attempt to
        #    perform request smuggling (Section 9.5) or response splitting
        #    (Section 9.4) and ought to be handled as an error.
        #
        # 2. If a message is received without Transfer-Encoding and with either
        #    multiple Content-Length header fields having differing
        #    field-values or a single Content-Length header field having an
        #    invalid value, then the message framing is invalid and the
        #    recipient MUST treat it as an unrecoverable error. If this is a
        #    request message, the server MUST respond with a 400 (Bad Request)
        #    status code and then close the connection.
        #
        # 3. If a valid Content-Length header field is present without
        #    Transfer-Encoding, its decimal value defines the expected message
        #    body length in octets. If the sender closes the connection or the
        #    recipient times out before the indicated number of octets are
        #    received, the recipient MUST consider the message to be incomplete
        #    and close the connection.
        #
        # 4. If this is a request message and none of the above are true, then
        #    the message body length is zero (no message body is present).
        #
        # TODO: This needs to handle Transfer-Encoding: chunked
        # TODO: This needs to handle the case where there are multiple
        #       Content-Length headers.
        # TODO: Should we sometimes mandate a Content-Length?

        assert self.headers_complete, (
            "Cannot determine body length without the headers"
        )

        content_length = self.headers.get(b"Content-Length", 0)
        try:
            content_length = int(content_length)
        except ValueError:
            raise BadRequest

        if content_length >= 0:
            return content_length
        else:
            raise BadRequest

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
        value = http11.ffi.buffer(value, vlen)[:]

        # TODO: We need to handle multiple values here, probably by collapsing
        #       them into a single value?
        assert field not in self.headers

        # Actually add the parsed value to our stored headers
        self.headers[field] = value

    def _cb_header_done(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == http11.ffi.NULL

        # Now that the headers have been parsed we can mark this has having
        # been completed.
        self.headers_complete = True

    def recv_body(self):
        # Calling recv_body before we've received any body data is invalid so
        # we'll assert that we have a buffer.
        assert self._buffer is not None, "Cannot recv_body without a body"

        # Make a view to our buffer, starting from the last place we read from,
        # this will enable us to return a view that contains only the data that
        # we have not yet returned.
        view = self._buffer.view(self._buffer_pos)

        # Advance our buffer position to the high water mark of the buffer
        self._buffer_pos = self._buffer.writepos

        return view

    def execute(self, data, length=None, offset=0):
        # If this parser is completed, then we don't care about processing
        # anymore data and we can just return a zero to signal we've parsed
        # None of the Content.
        if self.completed:
            return 0

        # If we were not given a length, then we assume we're to parse the
        # entire length of the data minus the offset
        if length is None:
            length = len(data) - offset

        # We only need to pass this data into our C parser if we haven't
        # completed parsing the headers yet
        if not self.headers_complete:
            # Actually parse the chunk of data we've been given. The return
            # value will be how much data was actually parsed.
            parsed = http11.lib.http_parser_execute(
                self._parser, data, length, offset,
            )
        else:
            # If we haven't parsed anything, then we've parsed 0 bytes
            parsed = 0

        # If we have finished parsing the headers, then we are parsing the
        # body, however we only need to actually parse the body if we have one.
        if self.headers_complete and self.body_length:
            # If we haven't created a buffer yet, then go ahead and create one
            # which has enough room for our entire request body.
            if self._buffer is None:
                self._buffer = zero_buffer.Buffer.allocate(self.body_length)

            # We need to figure out the correct offset from our data, this
            # should be our original offset, plus any data that we've parsed
            # in the headers
            body_offset = offset + parsed

            # Now we need to figure out the correct length from our data, this
            # should be our original length, minus any thing that we've
            # parsed already.
            body_length = length - parsed

            # TODO: Should we handle the case where we have a negative value
            #       specially? That should only happen if the c library parsed
            #       past where it was told too.
            # TODO: Should we handle the case where our body_length and
            #       body_offset will cause us to read past of the end of the
            #       data? Since we're using slices this won't actually do
            #       anything except cause us to return funky numbers for our
            #       parsed.
            if body_length > 0:
                # Add the remaining body into our buffer and add the amount
                # that has been added so that our count of bytes parsed is
                # accurate.
                # TODO: Should we optimize this to prevent copying it when
                #       the body_offset is 0, and body_length is len(data)?
                parsed += self._buffer.add_bytes(
                    data[body_offset:body_offset + body_length]
                )

        # Finally, return how much we've parsed so that the user can make
        # decisions about what to do with the rest of the data.
        return parsed
