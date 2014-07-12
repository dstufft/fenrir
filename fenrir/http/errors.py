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

import textwrap

import fenrir


class HTTPError(Exception):
    http_version = b"HTTP/1.1"
    status = (0, "Error")
    body = textwrap.dedent(
        """
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <title>{status[0]} {status[1]}</title>
          </head>
          <body>
            <h1 style="text-align: center;">{status[0]} {status[1]}</h1>
            <hr>
            <div style="text-align: center;">
              {software.__title__} {software.__version__}
            </div>
          </body>
        </html>
        """
    )

    def as_response(self):
        return (
            "{} {}".format(*self.status).encode("ascii"),
            {b"Content-Type": b"text/html; charset=\"ascii\""},
            [
                self.body.format(
                    status=self.status,
                    software=fenrir,
                ).encode("ascii"),
            ],
        )


class BadRequest(HTTPError):
    status = (400, "Bad Request")
