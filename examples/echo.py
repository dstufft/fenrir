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

from stein.protocol import HTTPServer


@asyncio.coroutine
def echo(data):
    yield from asyncio.sleep(2)
    return data


@asyncio.coroutine
def echo_app(request, body):
    data = yield from body.read()

    return (
        b"200 OK",
        {b"Is-Demo": b"Yes!", b"Multi-Value": [b"One", b"Two"]},
        [echo(data)],
    )


def main(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    server = loop.run_until_complete(
        loop.create_server(HTTPServer(echo_app), port=5000),
    )

    loop.run_until_complete(server.wait_closed())


if __name__ == "__main__":
    main()
