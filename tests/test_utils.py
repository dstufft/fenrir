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

import importlib

import pretend
import pytest

from fenrir.utils import resolve_app


def test_resolve_app_resolves(monkeypatch):
    app = pretend.stub()
    module = pretend.stub(myapp=app)
    monkeypatch.setattr(importlib, "import_module", lambda x: module)

    assert resolve_app("example:myapp") is app


def test_resolve_app_resolves_default(monkeypatch):
    app = pretend.stub()
    module = pretend.stub(app=app)
    monkeypatch.setattr(importlib, "import_module", lambda x: module)

    assert resolve_app("example") is app


def test_resolve_app_valid():
    with pytest.raises(ValueError):
        resolve_app("foo:bar:wat")
