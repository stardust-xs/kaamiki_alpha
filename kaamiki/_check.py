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

"""Utility of checking the latest version of Kaamiki."""

import json
import re
import subprocess
import sys
import urllib.request
from distutils.version import StrictVersion
from typing import Optional, Tuple

from pkg_resources import parse_version

from kaamiki.utils.common import network_available


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


def compare_version(package: str = "kaamiki") -> str:
    """Compares installed and latest stable version of Kaamiki."""
    name, current = _check_current(package)

    if network_available:
        package = name if name != package else package
        latest = _check_latest(package)
        latest = latest if latest else current

        if parse_version(current) == parse_version(latest):
            return ('You are using the latest version of '
                    f'{package}, v{latest}')
        elif parse_version(current) < parse_version(latest):
            return ('You are using an older version of {}, v{}\nHowever, v{} '
                    'is available for download. You should consider upgrading '
                    'using "pip install --upgrade {}" command.').format(
                        package, current, latest, package)
        else:
            return ('You are using the development version of {}, v{}\nIf '
                    'you want to roll back to the stable version consider '
                    'downgrading using "pip install {}" command.').format(
                        package, current, package)
    else:
        return ("No active internet connection is available at the moment. "
                f"Couldn't check for the latest version of {package}.")
