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

import pretend
import pytest

from fenrir.c.utils import Library


class TestLibrary:

    def test_doesnt_compile_on_creation(self):
        compile_module = pretend.call_recorder(lambda: None)
        ffi = pretend.stub(
            verifier=pretend.stub(
                compile_module=compile_module,
                _compile_module=compile_module,
            )
        )

        lib = Library(ffi)

        assert lib.lib is None
        assert compile_module.calls == []

    def test_prevents_compilation(self):
        compile_module = pretend.call_recorder(lambda: None)
        ffi = pretend.stub(
            verifier=pretend.stub(
                compile_module=compile_module,
                _compile_module=compile_module,
            )
        )

        lib = Library(ffi)

        with pytest.raises(RuntimeError):
            lib.ffi.verifier.compile_module()

        with pytest.raises(RuntimeError):
            lib.ffi.verifier._compile_module()

    def test_loads_lazily(self):
        foobar = pretend.stub()
        froblob = pretend.stub()
        loaded_lib = pretend.stub(foobar=foobar, froblob=froblob)
        ffi = pretend.stub(
            verifier=pretend.stub(
                load_library=pretend.call_recorder(lambda: loaded_lib),
            )
        )

        lib = Library(ffi)

        # Quick sanity check
        assert lib.lib is None
        assert lib.ffi.verifier.load_library.calls == []

        # Get some stuff from the underlying lib
        assert lib.foobar is foobar
        assert lib.froblob is froblob

        # Check that we've loaded the library (and only once)
        assert lib.lib is loaded_lib
        assert lib.ffi.verifier.load_library.calls == [pretend.call()]
