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

"""Check Kaamiki build for runtime errors."""

import json
import os
import re
import socket
import subprocess
import sys
import urllib.request
from distutils.version import StrictVersion
from typing import Optional, Tuple

from pkg_resources import parse_version

# Raise an exception if the environment is not correctly configured
# with platform-specific imports. All attempts to run Kaamiki on an
# incorrect environment will fail gracefully.
if os.name == "nt":
    # Attempt to load Windows based python imports, so that we can
    # raise an actionable error message if they are not found.
    modules = ["comtypes", "pywinauto", "win10toast"]
    missing = []

    for module in modules:
        try:
            import module
        except ImportError:
            missing.append(module)
    # See https://stackoverflow.com/a/19839338 for grammatical list
    # joining.
    if missing:
        _missing = ", ".join(missing[:-2] + [" and ".join(missing[-2:])])
        _modules = " ".join(missing)
        print(f"ImportError: Cannot import {_missing} module(s).\nKaamiki "
              f"requires that these module(s) be installed in your python "
              f"environment. You can install them using `pip install "
              f"{_modules}` command.")
        del missing
        sys.exit(0)

    try:
        from win32gui import GetForegroundWindow
        from win32process import GetWindowThreadProcessId
        from win32api import GetFileVersionInfo
        _PYWIN32_INSTALLED = True
    except ImportError:
        _PYWIN32_INSTALLED = False

    if not _PYWIN32_INSTALLED:
        print("ImportError: PyWin32 is not installed, and is required for "
              "running protocols.\nSee https://stackoverflow.com/a/20128310 "
              "for instructions on how to install PyWin32 on your system.")
        del _PYWIN32_INSTALLED
        sys.exit(0)
else:
    # TODO(xames3): Consider adding checks for Linux and MacOS builds.
    pass


def _connected(host: str = "8.8.8.8",
               port: int = 53,
               timeout: float = 10.0) -> bool:
    """
    Returns the status of network connectivity via socket connection.

    Args:
        host: Host IP address or Hostname of a webserver.
        port: Port of the webserver.
        timeout: Request timeout.

    Note:
        8.8.8.8 or google-public-dns-a.google.com, is public DNS for
        Google which is accessible via TCP port 53.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def _extract_details(command: str, parameter: str) -> str:
    """Extract required details."""
    return re.findall(f"({parameter.capitalize()}:)(.+)\n",
                      command)[0][-1].strip()


def _check_current(package: str) -> Tuple[str, str]:
    """Checks current installed version."""
    cmd = subprocess.run([sys.executable, "-m", "pip", "show", package],
                         stdout=subprocess.PIPE).stdout.decode("utf-8")
    return _extract_details(cmd, "name"), _extract_details(cmd, "version")


def _check_latest(package: str) -> Optional[str]:
    """Checks latest available version on PyPI."""
    url = f"https://pypi.org/pypi/{package}/json"
    data = json.load(urllib.request.urlopen(url))["releases"].keys()
    return sorted(data, key=StrictVersion, reverse=True)[0]


def _compare_version(package: str = "kaamiki", force: bool = False) -> None:
    """Compares installed and latest stable version of Kaamiki."""
    name, current = _check_current(package)

    if _connected:
        package = name if name != package else package
        latest = _check_latest(package)
        latest = latest if latest else current

        if parse_version(current) == parse_version(latest) and force:
            print(f"You are using the latest version of {package} v{latest}.")
        elif parse_version(current) < parse_version(latest):
            print(
                f"You are using an older version of {package} v{current}.\n"
                f"However, v{latest} is currently available for download. "
                f"You should consider upgrading to it with `pip install --"
                f"upgrade {package}` command."
            )
        elif parse_version(current) > parse_version(latest):
            print(
                f"You are using the development version of {package} v"
                f"{current}.\nIf you want to roll back to the stable "
                f"version, consider downgrading with `pip install "
                f"{package}` command."
            )
        else:
            return None
    else:
        if force:
            print(
                f"Internet connection is questionable at the moment. "
                f"Couldn't check for the latest version of {package}."
            )


_compare_version()
