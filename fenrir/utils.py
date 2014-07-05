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


def resolve_app(app_name):
    # First we need to determine the module and function name for our
    # application
    module_name, *leftover = app_name.split(":", 1)
    if len(leftover) > 1:
        raise ValueError("Cannot have more than one ':' in the app name")
    elif leftover:
        func_name = leftover[0]
    else:
        func_name = "app"

    # Then we need to actually import the module and get the application
    # callable from it.
    module = importlib.import_module(module_name)
    app = getattr(module, func_name)

    # Return our now resolved application object
    return app
