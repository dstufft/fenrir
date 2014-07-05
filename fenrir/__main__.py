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

import argparse
import sys

from fenrir.server import Server


def main(argv):
    parser = argparse.ArgumentParser(prog="fenrir")
    parser.add_argument("app")

    # Parse our options from the command line
    options = parser.parse_args(argv)

    # Create a server instance from our options
    server = Server(options.app)

    # Finally, spawn our server
    server.spawn()


def entrypoint():
    """
    Small wrapper for a setuptools entrypoint to pass sys.argv into main().
    """
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
