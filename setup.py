# Copyright (c) 2020 Kaamiki Developers. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ======================================================================

"""
Kaamiki

Kaamiki is a simple machine learning framework for obvious tasks.
"""
# TODO(xames3): Add a descriptive docstring which would help the
# users and developers alike to get an idea what and how kaamiki
# could assist them with right out of the box with very minimal
# efforts.

import os
import os.path as _os
import sys

# Raise active exceptions if the installing system environment is
# not configured correctly for kaamiki.
if sys.version_info < (3,):
  sys.exit("Python 2 has reached end-of-life and is no longer supported "
           "by Kaamiki.")

if sys.version_info < (3, 5):
  sys.exit("Kaamiki supports minimum python 3.6 and above. Kindly upgrade "
           "your python interpreter to a suitable version.")

if os.name == "nt" and sys.maxsize.bit_length() == 31:
  sys.exit("32-bit Windows Python runtime is not supported. Please switch "
           "to 64-bit Python.")

from setuptools import find_packages, setup

_NAME = "kaamiki"

# The version string is semver compatible and adheres to Semantic
# Versioning Specification (SemVer) starting with version 0.1.
# See https://semver.org/spec/v2.0.0.html for more help on it.
_VERSION = "1.0.3"


def _use_readme() -> str:
  """Use README.md for long description of kaamiki."""
  with open("README.md", "r") as file:
    return file.read()


# Flag which raises warning if the installed version of kaamiki
# is outdated or a nightly build if that matters.
_VERSION_FLAG = 0


def _cook() -> None:
  """Prepare the required directory structure while setting up."""
  # Create base directory for caching, logging and storing data of
  # kaamiki session.
  base = _os.expanduser(f"~/.{_NAME}/")
  if not _os.exists(base):
    os.mkdir(base)

  with open(os.path.join(base, "update"), "w") as _file:
    _file.write(f"version: {_VERSION}\n"
                f"check: {_VERSION_FLAG}")


with open("requirements.txt", "r") as requirements:
  if os.name != "nt":
    skip = ["psutil", "pywin32", "pypywin32", "pywinauto", "win10toast"]
    packages = [idx for idx in requirements if idx.rstrip() not in skip]

_DOCLINES = __doc__ if __doc__.count("\n") == 0 else __doc__.split("\n")

setup(
    name=_NAME,
    version=_VERSION,
    url="https://github.com/kaamiki/kaamiki",
    author="XAMES3",
    author_email="xames3.developer@gmail.com",
    maintainer_email="xames3.kaamiki@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3 :: Only",
    ],
    license="Apache Software License 2.0",
    description=" ".join(_DOCLINES[3:5]),
    long_description=_use_readme(),
    long_description_content_type="text/markdown",
    keywords="kaamiki python c++ machine learning pandas numpy cv2",
    zip_safe=False,
    install_requires=packages,
    python_requires="~=3.6",
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "kaamiki = kaamiki.parser:main",
        ],
    },
    platform=["Linux", "Windows", "macOS"],
)

_cook()
