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
"""
An example application which simply will simply echo everything sent to it.

This can be run using:

    PYTHONPATH=examples python -m fenrir echo:app
"""

import asyncio


@asyncio.coroutine
def echo(data):
    return data


@asyncio.coroutine
def app(request, body):
    data = yield from body.read()

    return (
        b"200 OK",
        {b"Is-Demo": b"Yes!", b"Multi-Value": [b"One", b"Two"]},
        [echo(data)],
    )
