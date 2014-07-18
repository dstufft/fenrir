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


def create_modulename(cdef_source, source, sys_version):
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


class Library:

    def __init__(self, ffi):
        self.ffi = ffi
        self._lib = None

        # This prevents the compile_module() from being called, the module
        # should have been compiled by setup.py
        def _compile_module(*args, **kwargs):
            raise RuntimeError("Cannot compile module during runtime")
        self.ffi.verifier.compile_module = _compile_module
        self.ffi.verifier._compile_module = _compile_module

    @property
    def lib(self):
        if self._lib is None:
            self._lib = self.ffi.verifier.load_library()
        return self._lib

    def __getattr__(self, name):
        return getattr(self.lib, name)
