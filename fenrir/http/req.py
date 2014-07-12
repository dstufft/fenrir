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

from fenrir.http.parser import HTTPParser


class Request:

    def __init__(self, body):
        self._parser = HTTPParser()
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
        return self._parser.headers

    @property
    def headers_complete(self):
        return self._parser.headers_complete

    @property
    def received(self):
        return self._parser.completed

    def add_bytes(self, data):
        if not data:
            return

        self._parser.execute(data)

        # If our headers are complete, feed any data we've gotten past the
        # headers into our body.
        if self.headers_complete:
            if self._parser.body_length:
                self.body.feed_data(self._parser.recv_body())

            # Determine if we've received the complete HTTP request, if we have
            # then we should close our stream reader because there is nothing
            # more to read.
            if self.received:
                self.body.feed_eof()

    def as_params(self):
        # TODO: This needs to not expose this class which is an internal detail
        #       and instead use a better data structure.
        return self, self.body
