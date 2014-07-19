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
import collections.abc
import itertools

from fenrir.http.errors import BadRequest


class Headers(collections.abc.Mapping):

    def __init__(self, headers):
        # TODO: Should we parse the header values to turn multiple headers on
        #       one line into a list?
        self._headers = collections.OrderedDict()
        self._real_keys = collections.OrderedDict()

        for key, value in headers:
            if not isinstance(key, bytes):
                raise TypeError("Headers only supports bytes for keys.")

            normalized_key = key.lower()
            self._real_keys.setdefault(normalized_key, key)
            self._headers.setdefault(normalized_key, []).append(value)

    def __repr__(self):
        return "Headers({})".format(
            list(
                itertools.chain.from_iterable(
                    (
                        ((self._real_keys[k], i) for i in v)
                        for k, v in self._headers.items()
                    )
                )
            )
        )

    def __getitem__(self, key):
        if not isinstance(key, bytes):
            raise TypeError("Headers only supports bytes for keys.")

        return self._headers[key.lower()]

    def __iter__(self):
        return iter(self._real_keys.values())

    def __len__(self):
        return len(self._headers)


class Request:

    def __init__(self, http_version, method, path, query, headers, body):
        self.http_version = http_version
        self.method = method
        self.path = path
        self.query = query
        self.headers = Headers(headers)
        self.body = body

        # RFC 7230 Section 3.3.3 - Ensure Valid Content-Length
        # If the Content-Length is specified then it must be a valid value,
        # this means it must be an integer and it must be >= 0.
        if b"Content-Length" in self.headers:
            content_lengths = self.headers[b"Content-Length"]

            # Ensure all values are valid integers and aren't non-sense
            try:
                content_lengths = [int(cl) for cl in content_lengths]
            except ValueError:
                raise BadRequest from None

            # Ensure all values are the same
            if len(set(content_lengths)) > 1:
                raise BadRequest

            # Ensure all values are >= 0
            if not all([cl >= 0 for cl in content_lengths]):
                raise BadRequest

            # De-duplicate extra values of Content-Length into a single value.
            self.headers = Headers(
                itertools.chain.from_iterable(
                    [
                        (
                            [(k, i) for i in v]
                            if k.lower() != b"content-length"
                            else [(k, v[0])]
                        )
                        for k, v in self.headers.items()
                    ]
                )
            )

        # RFC 7230 Section 5.4 - Ensure Host Header
        # HTTP/1.1 mandates the existence of a Host header on all requests,
        # while HTTP/1.0 does not, however due to the critical nature of
        # the Host header for virtual hosting nearly all HTTP/1.0 clients
        # will send a Host header anyways. We will be strict here and mandate
        # it for all requests.
        if b"Host" not in self.headers:
            raise BadRequest
        elif len(set(self.headers[b"Host"])) > 1:
            raise BadRequest

    def as_params(self):
        return (self, self.body)
