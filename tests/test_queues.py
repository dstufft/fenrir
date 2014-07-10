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

import pytest

from fenrir.queues import CloseableQueue, QueueClosed


class TestCloseableQueue:

    def test_queue_closes(self):
        queue = CloseableQueue()
        assert not queue.closed
        queue.close()
        assert queue.closed

    def test_queue_works_when_open(self):
        queue = CloseableQueue()
        queue.put_nowait("Foo")

        assert queue.get_nowait() == "Foo"

    def test_queue_errors_when_closed(self):
        queue = CloseableQueue()
        queue.close()

        with pytest.raises(QueueClosed):
            queue.put_nowait("Foo")
