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
This file has been adapted from Mongrel2's tests/http11_tests.c, it is more or
less a translation to using cffi and pytest to test the underlying HTTP
parser.

This is primarily intended to ensure that any modifications we make to the
parser do not break any tests that Mongrel2 had for the parser.
"""

import glob
import os.path

import pytest

from fenrir.c import http11


@http11.element_cb
def debug_element_cb(data, at, length):
    assert data == http11.ffi.NULL
    http11.ffi.buffer(at, length)[:]


@http11.field_cb
def debug_field_cb(data, field, flen, value, vlen):
    assert data == http11.ffi.NULL
    http11.ffi.buffer(field, flen)[:]
    http11.ffi.buffer(value, vlen)[:]


@pytest.fixture
def parser():

    p = http11.ffi.new("http_parser *")
    p.http_field = debug_field_cb
    p.request_method = debug_element_cb
    p.request_uri = debug_element_cb
    p.fragment = debug_element_cb
    p.request_path = debug_element_cb
    p.query_string = debug_element_cb
    p.http_version = debug_element_cb
    p.header_done = debug_element_cb

    http11.lib.http_parser_init(p)

    return p


def test_http11_parser_basics(parser):
    rc = http11.lib.http_parser_finish(parser)
    assert rc == 0, "Should NOT be finished if nothing parsed."

    rc = http11.lib.http_parser_has_error(parser)
    assert rc == 0, "Should not have an error at the beginning."

    rc = http11.lib.http_parser_is_finished(parser)
    assert rc == 0, "Should not be finished since never handed anything."


@pytest.mark.parametrize(
    "filename",
    glob.glob(os.path.join(os.path.dirname(__file__), "canned", "*")),
)
def test_parser_thrashing(parser, filename):
    with open(filename, "rb") as fp:
        data = fp.read()

    parsed = 0

    while parsed < len(data):
        delta = http11.lib.http_parser_execute(parser, data, len(data), parsed)
        parsed += delta

        if delta == 0:
            break

        http11.lib.http_parser_finish(parser)
        http11.lib.http_parser_has_error(parser)

        # Reset for next try
        http11.lib.http_parser_init(parser)
