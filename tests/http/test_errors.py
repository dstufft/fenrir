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

import fenrir

from fenrir.http.errors import HTTPError, BadRequest


class TestHTTPError:

    @pytest.mark.parametrize(
        ("error", "expected_status"),
        [
            (HTTPError, b"0 Error"),
            (BadRequest, b"400 Bad Request"),
        ],
    )
    def test_as_response(self, error, expected_status):
        status, headers, body = error().as_response()
        expected_body = (
            error().body.format(status=error().status, software=fenrir)
            .encode("ascii")
        )

        assert status == expected_status
        assert headers == {b"Content-Type": b"text/html; charset=\"ascii\""}
        assert body == [expected_body]
