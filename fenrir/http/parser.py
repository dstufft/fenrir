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

from fenrir.http import c


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
        self.completed = False
        self._buffer = None

        # Create a http_parser struct so to act as a bag of data to store
        # information about what we're parsing into
        self._parser = c.ffi.new("http_parser *")

        # Initialize our http_parser struct
        c.lib.http_parser_init(self._parser)

        # Create our callback functions, these are FFI callback instances which
        # we store on our instance because if we allow them to get garbage
        # collected before they're called by the C code.
        self._cb_header_done = c.element_cb(self._cb_header_done)
        self._cb_http_version = c.element_cb(self._cb_http_version)
        self._cb_request_method = c.element_cb(self._cb_request_method)
        self._cb_request_path = c.element_cb(self._cb_request_path)
        self._cb_query_string = c.element_cb(self._cb_query_string)
        self._cb_http_field = c.field_cb(self._cb_http_field)

        # Actually register our callbacks with our http_parser instance
        self._parser.header_done = self._cb_header_done
        self._parser.http_version = self._cb_http_version
        self._parser.request_method = self._cb_request_method
        self._parser.request_path = self._cb_request_path
        self._parser.query_string = self._cb_query_string
        self._parser.http_field = self._cb_http_field

    def _cb_http_version(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == c.ffi.NULL

        self.http_version = c.ffi.buffer(at, length)[:]

    def _cb_request_method(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == c.ffi.NULL

        self.method = c.ffi.buffer(at, length)[:]

    def _cb_request_path(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == c.ffi.NULL

        self.path = c.ffi.buffer(at, length)[:]

    def _cb_query_string(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == c.ffi.NULL

        self.query = c.ffi.buffer(at, length)[:]

    def _cb_http_field(self, data, field, flen, value, vlen):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == c.ffi.NULL

        # We need to get the field name and the value from our buffers so that
        # we can use that data as our headers.
        field = c.ffi.buffer(field, flen)[:]
        value = c.ffi.buffer(value, vlen)[:]

        # TODO: We need to handle multiple values here, probably by collapsing
        #       them into a single value?
        assert field not in self.headers

        # Actually add the parsed value to our stored headers
        self.headers[field] = value

    def _cb_header_done(self, data, at, length):
        # Will this always be NULL? I have no idea about it seems to be, so
        # we'll assert against it being NULL just to make sure.
        assert data == c.ffi.NULL

        # Now that the headers have been parsed we can mark this has having
        # been completed.
        self.headers_complete = True

    def recv_body(self):
        # We only want to create a view and return any data if we have a buffer
        # and it has some data, otherwise we'll just return a b""
        if self._buffer is not None and self._buffer.writepos:
            # Make our buffer a view, this will allow the calling code to treat
            # it more like a bytes object.
            view = self._buffer.view()

            # Figure out how much of the body is left that we haven't already
            # added to the buffer
            left = self._buffer.capacity - self._buffer.writepos

            # Figure out if we have any data left to be received, if so we'll
            # create a new, smaller buffer which will be equal to the size of
            # our expected body minus what we've already added to the buffer.
            # This will allow our buffer to grow increasingly smaller as things
            # are read off it.
            if left:
                # TODO: Figure out if this is a good idea, or if it'd be better
                #       to make smaller buffers that we collate into, or if
                #       it'd be better to track how much we've pulled off the
                #       buffer and just return a partial view.
                self._buffer = zero_buffer.Buffer.allocate(left)
            else:
                # We have no content left to pull off the buffer, so we'll
                # just mark this parser as complete and be done with it.
                self.completed = True

            return view
        else:
            return b""

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
            parsed = c.lib.http_parser_execute(
                self._parser, data, length, offset,
            )
        else:
            # If we haven't parsed anything, then we've parsed 0 bytes
            parsed = 0

        # If we have finished parsing the headers, then we are parsing the
        # body, however we only need to actually parse the body if we have one.
        # For HTTP/1.1 we mandate a Content-Length for requests or else we
        # assume 0.
        # TODO: Verify that the Content-Length Mandate is accurate, and add
        #       references to that fact.
        # TODO: We should probably be smart about turning Content-Length into
        #       and integer and not just blindly int() it.
        if (self.headers_complete
                and int(self.headers.get(b"Content-Length", 0))):
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
                # If we haven't created a buffer yet, then go ahead and create
                # one which has enough room for our entire request body.
                # TODO: Should we move this to the header callback?
                if self._buffer is None:
                    self._buffer = zero_buffer.Buffer.allocate(
                        int(self.headers[b"Content-Length"]),
                    )

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
