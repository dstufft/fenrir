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

from fenrir.protocol import HTTPServer


class TestHTTPServer:

    def test_basic_factory(self):
        protocol_instance = pretend.stub()
        protocol = pretend.call_recorder(lambda cb, loop: protocol_instance)
        callback = pretend.stub()

        factory = HTTPServer(callback)
        factory.protocol_class = protocol

        assert factory() is protocol_instance
        assert factory.protocol_class.calls == [
            pretend.call(callback, loop=None),
        ]
