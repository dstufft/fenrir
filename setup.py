#!/usr/bin/env python
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

from setuptools import setup, find_packages


meta = {}
with open("stein/__init__.py") as fp:
    exec(fp.read(), meta)


with open("README.rst") as fp:
    long_description = fp.read()


setup(
    name=meta["__title__"],
    version=meta["__version__"],

    description=meta["__summary__"],
    long_description=long_description,
    license=meta["__license__"],
    url=meta["__url__"],

    author=meta["__author__"],
    author_email=meta["__email__"],

    classifiers=[
        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],

    packages=find_packages(),

    install_requires=[
        "http-parser",
    ],

    zip_safe=False,
)
