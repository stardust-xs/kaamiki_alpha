# Copyright (c) 2020 Kaamiki Authors. All rights reserved.
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
# TODO(xames3): Add more elaborative docstring.

import os
import sys

# Raise passive exceptions if the system environment is not configured
# correctly for Kaamiki runtime.
if sys.version_info < (3,):
    print("Python 2 has reached end-of-life and is no longer supported by "
          "Kaamiki.")
    quit()

if sys.version_info < (3, 5):
    print("Kaamiki supports minimum python 3.6 and above. Kindly upgrade "
          "your python interpreter to a suitable version.")
    quit()

if os.name == "nt" and sys.maxsize.bit_length() == 31:
    print("32-bit Windows Python runtime is not supported. Please switch "
          "to 64-bit Python.")
    quit()

from setuptools import find_packages, setup

from kaamiki import _NAME

# This version string is semver compatible & adheres to Semantic
# Versioning Specification (SemVer) starting with version 0.1.
# You can read more about it here: https://semver.org/spec/v2.0.0.html
_VERSION = "1.0.1"

_DOCLINES = __doc__ if __doc__.count("\n") == 0 else __doc__.split("\n")


def use_readme() -> str:
    """Use README.md for long description of the package."""
    with open("README.md", "r") as file:
        return file.read()


def cook() -> None:
    """Prepares the required directory structure."""
    base = os.path.expanduser("~/.kaamiki/")
    # Create base directory for logging and storing data or cache files.
    if not os.path.exists(base):
        os.mkdir(base)

    with open(os.path.join(base, "update"), "w") as _file:
        _file.write(f"installed_version={_VERSION}\ncheck_status=0")


with open("requirements.txt", "r") as requirements:
    packages = [package.rstrip() for package in requirements]
    # Skip downloading packages meant for Windows when running on a
    # Non Windows system. This ensures proper packages are downloaded
    # for the respective OS.
    if os.name != "nt":
        skip = ["psutil", "pywin32", "pypywin32", "pywinauto", "win10toast"]
        packages = [idx for idx in packages if idx not in skip]

try:
    setup(
        name=_NAME,
        version=_VERSION,
        url="https://github.com/kaamiki/kaamiki",
        author="XAMES3",
        author_email="xames3.developer@gmail.com",
        maintainer_email="xames3.kaamiki@gmail.com",
        # PyPI package information.
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: MacOS X",
            "Environment :: Win32 (MS Windows)",
            "Environment :: X11 Applications",
            "Environment :: X11 Applications :: Gnome",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Information Technology",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: Apache Software License",
            "Natural Language :: English",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows :: Windows 10",
            "Operating System :: POSIX",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Unix Shell",
            "Topic :: Desktop Environment :: Gnome",
            "Topic :: Home Automation",
            "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
            "Topic :: Multimedia :: Video :: Capture",
            "Topic :: Office/Business :: Scheduling",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Scientific/Engineering :: Image Recognition",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Scientific/Engineering :: Mathematics",
            "Topic :: Software Development",
            "Topic :: System :: Archiving",
            "Topic :: System :: Monitoring",
            "Topic :: System :: Networking :: Monitoring :: Hardware Watchdog",
            "Topic :: System :: Networking :: Time Synchronization",
            "Topic :: System :: Operating System Kernels :: Linux",
        ],
        license="Apache Software License 2.0",
        description=" ".join(_DOCLINES[3:5]),
        long_description=use_readme(),
        long_description_content_type="text/markdown",
        keywords="kaamiki python c++ machine learning pandas numpy cv2",
        zip_safe=False,
        install_requires=packages,
        python_requires="~=3.6",
        include_package_data=True,
        packages=find_packages(),
        platform=["Windows", "Linux", "Mac OS"],
    )
except Exception as error:
    print("An error occurred while installing Kaamiki.\nSee "
          "https://github.com/kaamiki/kaamiki for instructions on how "
          "install it on your system incase of any problems. If the "
          "error still persists, please feel free to raise an issue "
          "over here: https://github.com/kaamiki/kaamiki/issues.")
else:
    cook()
