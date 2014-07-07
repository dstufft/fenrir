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


class QueueClosed(Exception):
    pass


class CloseableQueue(asyncio.Queue):
    """
    A asyncio.Queue subclass which supports being closed. Once a CloseableQueue
    has been closed no new items will be allowed to be placed onto the queue.
    """

    def __init__(self, *args, **kwargs):
        self._closed = False
        super().__init__(*args, **kwargs)

    @property
    def closed(self):
        return self._closed

    def close(self):
        self._closed = True

    def _put(self, item):
        if self._closed:
            raise QueueClosed
        return super()._put(item)
