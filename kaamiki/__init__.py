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

import os

_NAME = "kaamiki"

# Raise an exception if the environment is not correctly configured
# with platform-specific imports. All attempts to run Kaamiki will
# fail gracefully.
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
        print("ImportError: Cannot import {} module(s).\nKaamiki requires "
              "that these module(s) be installed in your python environment. "
              "You can install them with `pip install {}`".format(_missing,
                                                                  _modules))
        del missing
        quit()

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
        quit()
else:
    # TODO(xames3): Consider adding checks for Linux and Mac OS builds.
    pass
