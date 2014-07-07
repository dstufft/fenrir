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

import binascii
import functools
import os.path
import sys

from cffi import FFI
from cffi.verifier import Verifier


# Write out our cdef to bind data to our FFI instance
CDEF = """
    typedef void (*element_cb)(void *data, const char *at, size_t length);
    typedef void (*field_cb)(void *data, const char *field, size_t flen,
                             const char *value, size_t vlen);

    typedef struct http_parser {
        int cs;
        size_t body_start;
        int content_len;
        size_t nread;
        size_t mark;
        size_t field_start;
        size_t field_len;
        size_t query_start;
        int xml_sent;
        int json_sent;

        void *data;

        field_cb http_field;
        element_cb request_method;
        element_cb request_uri;
        element_cb fragment;
        element_cb request_path;
        element_cb query_string;
        element_cb http_version;
        element_cb header_done;
    } http_parser;

    int http_parser_init(http_parser *parser);
    int http_parser_finish(http_parser *parser);
    size_t http_parser_execute(http_parser *parser, const char *data,
                               size_t len, size_t off);
    int http_parser_has_error(http_parser *parser);
    int http_parser_is_finished(http_parser *parser);
"""

SOURCE = """
    #include <http11/http11_parser.h>
"""


def _create_modulename(cdef_source, source, sys_version):
    """
    cffi creates a modulename internally that incorporates the cffi version.
    This will cause Fenrir's wheels to break when the version of cffi
    the user has does not match what was used when building the wheel. To
    resolve this we build our own modulename that uses most of the same code
    from cffi but elides the version key.
    """
    key = "\x00".join([sys_version[:3], source, cdef_source])
    key = key.encode("utf-8")
    k1 = hex(binascii.crc32(key[0::2]) & 0xffffffff)
    k1 = k1.lstrip("0x").rstrip("L")
    k2 = hex(binascii.crc32(key[1::2]) & 0xffffffff)
    k2 = k2.lstrip("0").rstrip("L")
    return "_cffi_{0}{1}".format(k1, k2)


# Build our FFI instance
ffi = FFI()
ffi.cdef(CDEF)

# We'll create a few partial functions here which can be used to register some
# callbacks that we'll need later
element_cb = functools.partial(
    ffi.callback,
    "void(void *data, const char *at, size_t length)",
)

field_cb = functools.partial(
    ffi.callback,
    (
        "void(void *data, const char *field, size_t flen, const char *value, "
        "size_t vlen)"
    ),
)


# We need to locate our sources, we have embedded the http parser from mongrel2
# so in this case our sources are located right alongside this file.
_bundled_dir = os.path.dirname(__file__)


# Construct a Verifier manually, this will prevent the ffi instance from
# attempting to load the library, which would trigger a compile normally if it
# can't be loaded, which we want to delay so it doesn't happen on import. This
# will enable us to import this module, and use it in our setup.py to get the
# Extension object to allow distutils to build it normally.
ffi.verifier = Verifier(
    ffi,

    SOURCE,

    # This needs to match the value in setup.py
    ext_package="fenrir",

    # Fix the fact that CFFI doesn't sanely work when you don't have the exact
    # version installed that a library was built against.
    modulename=_create_modulename(CDEF, SOURCE, sys.version),

    # We want to compile the http_parser.c instead of trying to link against it
    # or anything like that.
    sources=[
        os.path.join(_bundled_dir, "http11/http11_parser.c"),
    ],

    # We need to include the bundled dir so that we can include the header
    # files located in it.
    include_dirs=[
        _bundled_dir,
    ],
)


class Library:

    def __init__(self, ffi):
        self.ffi = ffi
        self._initialized = False

        # This prevents the compile_module() from being called, the module
        # should have been compiled by setup.py
        def _compile_module(*args, **kwargs):
            raise RuntimeError("Cannot compile module during runtime")
        self.ffi.verifier._compile_module = _compile_module

    def __getattr__(self, name):
        if not self._initialized:
            self._lib = self.ffi.verifier.load_library()
            self._initialized = True

        # redirect attribute access to the underlying lib
        return getattr(self._lib, name)


# We use a lazily-loading Library class to wrap the ffi library. We do this
# because otherwise importing this module, which we need to do in order to get
# the Extension object, will trigger CFFI to implicitly compile the object.
# Using this will disable the implicit compilation and delay the attempt to
# load the library until the first time a method is actually called on the
# lib, instead of when the lib is created/verified.
lib = Library(ffi)
