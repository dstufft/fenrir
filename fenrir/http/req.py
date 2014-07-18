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

import collections.abc

from fenrir.http.errors import BadRequest
from fenrir.http.parser import HTTPParser


def _header_parse(value, delim=b","):
    # Escape any quotes inside of the value if there are quotes in it and we
    # need to quote it because of a delimiter character.
    if b"\"" in value and delim in value:
        value = value.replace(b"\"", b"\\\"")

    if delim in value:
        value = b"\"" + value + b"\""

    return value


def _header_join(header, values):
    if header.lower() == b"cookie":
        return b"; ".join(_header_parse(v, b";") for v in values)
    else:
        return b",".join(_header_parse(v) for v in values)


class Headers(collections.abc.Mapping):

    def __init__(self, headers):
        for key in headers:
            if not isinstance(key, bytes):
                raise TypeError("Headers only supports bytes for keys.")

        self._raw_headers = {k: _header_join(k, v) for k, v in headers.items()}
        self._normalized_keys = {k.lower(): k for k in self._raw_headers}

    def __repr__(self):
        return "<Headers {}>".format(self._raw_headers)

    def __getitem__(self, key):
        if not isinstance(key, bytes):
            raise TypeError("Headers only supports bytes for keys.")

        real_key = self._normalized_keys.get(key.lower(), None)

        if real_key is None:
            raise KeyError(key)

        return self._raw_headers[real_key]

    def __iter__(self):
        return iter(self._raw_headers)

    def __len__(self):
        return len(self._raw_headers)


class Request:

    def __init__(self, body):
        self._parser = HTTPParser()
        self._validated = False
        self._headers = None
        self.body = body

    @property
    def http_version(self):
        return self._parser.http_version

    @property
    def method(self):
        return self._parser.method

    @property
    def path(self):
        return self._parser.path

    @property
    def query(self):
        return self._parser.query

    @property
    def headers(self):
        assert self.headers_complete, (
            "Headers must be complete before accessing them."
        )

        if self._headers is None:
            self._headers = Headers(self._parser.headers)

        return self._headers

    @property
    def headers_complete(self):
        return self._parser.headers_complete

    @property
    def received(self):
        return self._parser.completed

    def add_bytes(self, data):
        if not data:
            return

        parsed = self._parser.execute(data)

        # If our headers are complete, feed any data we've gotten past the
        # headers into our body.
        if self.headers_complete:
            # Validate our request if it hasn't already been validated.
            if not self._validated:
                self.validate()

            if self._parser.body_length:
                self.body.feed_data(self._parser.recv_body())

            # Determine if we've received the complete HTTP request, if we have
            # then we should close our stream reader because there is nothing
            # more to read.
            if self.received:
                self.body.feed_eof()

        # Return any data that we haven't parsed
        return data[parsed:]

    def validate(self):
        assert self.headers_complete, (
            "Cannot validate a request until all headers are received"
        )

        # RFC 7230 Section 3.3.3 - Ensure Valid Content-Length
        #   If the Content-Length is specified then it must be a valid value,
        #   this means it must be an integer and it must be >= 0.
        content_length = self.headers.get(b"Content-Length")
        if content_length is not None:
            try:
                content_length = int(content_length)
            except ValueError:
                raise BadRequest from None

            if content_length < 0:
                raise BadRequest

        # RFC 7230 Section 5.4 - Ensure Host Header
        #   HTTP/1.1 mandates the existence of a Host header on all requests,
        #   while HTTP/1.0 does not, however due to the critical nature of
        #   the Host header for virtual hosting nearly all HTTP/1.0 clients
        #   will send a Host header anyways. We will be strict here and mandate
        #   it for all requests.
        # TODO: Should the *value* of the Host header have any sort of
        #       validation?
        if b"Host" not in self.headers:
            raise BadRequest

        self._validated = True

    def as_params(self):
        # TODO: This needs to not expose this class which is an internal detail
        #       and instead use a better data structure.
        return self, self.body
