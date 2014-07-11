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

import sys

import pretend
import pytest

from fenrir import __main__


@pytest.mark.parametrize(
    ("argv", "options"),
    [
        (["example:app"], (["example:app"], {"bind": None})),
        (
            ["example:app", "-b", "0.0.0.0:5000"],
            (["example:app"], {"bind": ["0.0.0.0:5000"]}),
        ),
    ],
)
def test_main(argv, options, monkeypatch):
    server_obj = pretend.stub(spawn=pretend.call_recorder(lambda: None))
    server_cls = pretend.call_recorder(lambda *a, **kw: server_obj)

    monkeypatch.setattr(__main__, "Server", server_cls)

    __main__.main(argv)

    assert server_cls.calls == [pretend.call(*options[0], **options[1])]
    assert server_obj.spawn.calls == [pretend.call()]


def test_entrypoint(monkeypatch):
    exitcode = pretend.stub()
    main = pretend.call_recorder(lambda argv: exitcode)
    argv = ["fenrir", "-b", "0.0.0.0:8000"]

    monkeypatch.setattr(__main__, "main", main)
    monkeypatch.setattr(sys, "argv", argv)

    assert __main__.entrypoint() is exitcode
    assert main.calls == [pretend.call(["-b", "0.0.0.0:8000"])]
