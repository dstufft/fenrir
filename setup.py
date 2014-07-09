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

import os.path

from distutils.command.build import build
from distutils.command.build_clib import build_clib

from setuptools import find_packages, setup
from setuptools.command.install import install


CFFI_DEPENDENCY = "cffi>=0.8"


def get_ext_modules():
    from fenrir.http import http11
    return [http11.ffi.verifier.get_extension()]


def get_include_dirs(include_dirs):
    if include_dirs is None:
        include_dirs = []

    include_dirs.append(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "bundled",
        )
    )

    return include_dirs


class CFFIBuild(build):
    """
    This class exists, instead of just providing ``ext_modules=[...]`` directly
    in ``setup()`` because importing cryptography requires we have several
    packages installed first.

    By doing the imports here we ensure that packages listed in
    ``setup_requires`` are already installed.
    """

    def finalize_options(self):
        self.distribution.ext_modules = get_ext_modules()
        self.distribution.include_dirs = get_include_dirs(
            self.distribution.include_dirs,
        )
        build.finalize_options(self)


class CFFIInstall(install):
    """
    As a consequence of CFFIBuild and it's late addition of ext_modules, we
    need the equivalent for the ``install`` command to install into platlib
    install-dir rather than purelib.
    """

    def finalize_options(self):
        self.distribution.ext_modules = get_ext_modules()
        self.distribution.include_dirs = get_include_dirs(
            self.distribution.include_dirs,
        )
        install.finalize_options(self)


class HTTP1BuildCLib(build_clib):

    def build_libraries(self, *args, **kwargs):
        # Stash the initial values here
        compiler = self.compiler.compiler
        compiler_so = self.compiler.compiler_so

        # mongrel2's http11 parser does not build correctly with the
        # -Werror=declaration-after-statement option declared, so we'll ensure
        # that we don't have it specified.
        self.compiler.compiler = [
            x for x in self.compiler.compiler
            if x != "-Werror=declaration-after-statement"
        ]
        self.compiler.compiler_so = [
            x for x in self.compiler.compiler_so
            if x != "-Werror=declaration-after-statement"
        ]

        # Go ahead and finish building the libraries
        ret = build_clib.build_libraries(self, *args, **kwargs)

        # Undo our changes
        self.compiler.compiler = compiler
        self.compiler.compiler_so = compiler_so

        return ret


meta = {}
with open("fenrir/__init__.py") as fp:
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
        CFFI_DEPENDENCY,
        "zero_buffer",
    ],

    setup_requires=[
        CFFI_DEPENDENCY,
    ],

    # Build the mongrel2 http parser
    libraries=[
        (
            "http11",
            {
                "sources": ["bundled/http11/http11_parser.c"],
                "include_dirs": ["bundled"],
            },
        ),
    ],

    # These are needed so that CFFI can correctly function
    zip_safe=False,
    ext_package="fenrir",
    cmdclass={
        "build": CFFIBuild,
        "build_clib": HTTP1BuildCLib,
        "install": CFFIInstall,
    }
)
