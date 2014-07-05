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
import collections
import re

from fenrir.protocol import HTTPServer
from fenrir.utils import resolve_app


Bind = collections.namedtuple("Bind", ["host", "port"])


_bind_regex = re.compile(
    r"^(?:\[(?P<host_6>.+)\]|(?P<host_4>[^:]+))(?::(?P<port>[0-9]+))?$",
)


class Server:

    def __init__(self, app, bind=None):
        if isinstance(app, str):
            app = resolve_app(app)

        if bind is None:
            bind = ["localhost:8000"]

        bind = [
            Bind(x[0], int(x[1]) if len(x) > 1 else 8000)
            for x in (
                tuple(filter(None, _bind_regex.search(b).groups()))
                for b in bind
            )
        ]

        self.app = app
        self.bind = bind

        self._servers = []

    def spawn(self):
        loop = asyncio.get_event_loop()

        for bind in self.bind:
            self._servers.append(
                loop.run_until_complete(
                    loop.create_server(
                        HTTPServer(self.app, loop=loop),
                        host=bind.host,
                        port=bind.port,
                    ),
                )
            )

        # Wait for all of the servers to be closed before exiting the server
        loop.run_until_complete(
            asyncio.wait([s.wait_closed() for s in self._servers])
        )
