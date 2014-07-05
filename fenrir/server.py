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

import asyncio

from fenrir.protocol import HTTPServer
from fenrir.utils import resolve_app


class Server:

    def __init__(self, app):
        if isinstance(app, str):
            app = resolve_app(app)

        self.app = app

    def spawn(self):
        loop = asyncio.get_event_loop()
        server = loop.run_until_complete(
            loop.create_server(HTTPServer(self.app), port=5000),
        )
        loop.run_until_complete(server.wait_closed())
