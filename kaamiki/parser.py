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

"""Utility for interacting with Kaamiki via parser."""

import argparse
import itertools
import os
import sys
from textwrap import TextWrapper as _wrapper
from typing import Any, List, Tuple


class CommandLineParser(argparse.ArgumentParser):
  """
  Kaamiki Command Line Parser

  The `CommandLineParser` is a command line utility for using
  kaamiki's features without writing any code. Python's built
  in ArgumentParser is great but it blocks a couple of things
  that could help the user to navigate to the tools with more
  ease.
  Hence, the class aims to solve this problem and provide lot
  more details and decriptions for using each* command.
  """

  def __init__(self, *args: Any, **kwargs: Any) -> None:
    """Instantiate class."""
    self._width = round(os.get_terminal_size().columns / 1.3)
    self._program = {key: kwargs[key] for key in kwargs}
    # self._commands and self._options need to be initialized
    # first before calling `__init__()` of the inherited base
    # class, as the `argparse.ArgumentParser.__init__()` sets
    # `add_help=True` by default which allows execution of
    # add_argument("-h", "--help").
    self._commands = []
    self._options = []

    super().__init__(*args, **kwargs)

  def add_argument(self, *args: Any, **kwargs: Any) -> None:
    """
    Add arguments as inputs for parsing.

    This method defines the collection of input arguments.
    These arguments could be positional, optional or could
    be argument `values` passed to a method.

    Example:
      xames3@kaamiki:~$ kaamiki arg_1 --arg_2 ...
    """
    super().add_argument(*args, **kwargs)
    argument = {key: kwargs[key] for key in kwargs}
    # Prepare list of all command arguments i.e arguments with
    # only one name and not starting with `-` and are provided
    # as positional arguments to a method (values provided to
    # the `dest=` argument).
    if len(args) == 0 or (len(args) == 1 and
                          isinstance(args[0], str) and not
                          args[0].startswith("-")):
      argument["name"] = args[0] if len(args) > 0 else argument["dest"]
      self._commands.append(argument)
      return None

    # Prepare list of optional arguments i.e arguments with one or
    # more flags starting with `-` provided as positional argument
    # to a method.
    argument["flags"] = [arg for arg in args]
    self._options.append(argument)

  def format_usage(self) -> str:
    """
    Format helpful usage text.

    It defines the usage block and provides helpful description
    along with the syntax of using the particular command.

    Note:
      Not every command has usage information.
    """
    prefix = "Usage:\n  "
    # Use the below block if `usage` is provided.
    if "usage" in self._program:
      wrapper = _wrapper(self._width)
      wrapper.initial_indent = prefix
      wrapper.subsequent_indent = len(prefix) * " "
      if self._program["usage"] == "" or str.isspace(self._program["usage"]):
        return wrapper.fill("No usage information available.")
      return wrapper.fill(self._program["usage"])

    if "prog" in self._program and \
            self._program["prog"] != "" and not \
            str.isspace(self._program["prog"]):
      prog = self._program["prog"]
    else:
      prog = os.path.basename(sys.argv[0])

    usage = []
    usage.append(prefix)
    for command in self._commands[:4]:
      if "metavar" in command:
        usage.append(f"{prog} {command['metavar']} [options] ...")
      else:
        usage.append(f"{prog} {command['name']} [options] ...")
      usage.append("\n  ")

    return "".join(usage[:-1])

  def format_help(self) -> Tuple[List[str], ...]:
    """
    Return blocks of codes to use while displaying help text.

    It returns modular (tuple od strings) snippets of help text
    that are used for displaying the help.
    """
    description, commands, options, epilog = [], [], [], []
    args_len = desc_len = 0
    # Wrap epilog and the command description into a paragraph if
    # the string exceeds a set width. This ensures consistency in
    # the informative help texts.
    epilog_wrapper = _wrapper(self._width, replace_whitespace=False)
    desc_wrapper = _wrapper(self._width, replace_whitespace=False)
    desc_wrapper.subsequent_indent = 2 * " "
    # Add description if provided.
    if "description" in self._program and \
            self._program["description"] != "" and not \
            str.isspace(self._program["description"]):
      description.append("\nDescription:\n  ")
      description.extend(desc_wrapper.wrap(self._program["description"]))
      description.append("\n")

    for command in self._commands:
      if "metavar" in command:
        command["left"] = command["metavar"]
      else:
        command["left"] = command["name"]

    for option in self._options:
      if "action" in option and (option["action"] == "store_true" or
                                 option["action"] == "store_false"):
        option["left"] = str.join(", ", option["flags"])
      else:
        _flags = []
        for item in option["flags"]:
          if "metavar" in option:
            _flags.append(f"{item} <{option['metavar']}>")
          elif "dest" in option:
            _flags.append(f"{item} {option['dest'].upper()}")
          else:
            _flags.append(item)
        option["left"] = str.join(", ", _flags)

    for argument in self._commands + self._options:
      if "help" in argument and argument["help"] != "" and not \
              str.isspace(argument["help"]) and \
              "default" in argument and argument["default"] != \
              argparse.SUPPRESS:
        if isinstance(argument["default"], str):
          argument["right"] = argument["help"] + " " + \
              f"(Default: {argument['default']})"
        else:
          argument["right"] = argument["help"] + " " + \
              f"(Default: {argument['default']})"
      elif "help" in argument and argument["help"] != "" and not \
              str.isspace(argument["help"]):
        argument["right"] = argument["help"]
      elif "default" in argument and argument["default"] != argparse.SUPPRESS:
        if isinstance(argument["default"], str):
          argument["right"] = f"Default: '{argument['default']}'"
        else:
          argument["right"] = f"Default: {str(argument['default'])}"
      else:
        argument["right"] = "No description available."

      args_len = max(args_len, len(argument["left"]))
      desc_len = max(desc_len, len(argument["right"]))

    # Calculate maximum width required for displaying the args and
    # their respective descriptions. We are limiting the width of
    # args to maximum of self._width / 2. We use max() to prevent
    # negative values.
    args_width = args_len
    desc_width = max(0, self._width - args_width - 4)
    if (args_width > int(self._width / 2) - 4):
      args_width = max(0, int(self._width / 2) - 4)
      desc_width = int(self._width / 2)

    # Define template with two leading spaces and two trailing
    # spaces (spaces between args and description).
    template = "  %-" + str(args_width) + "s  %s"

    # Wrap text for args and description parts by splitting the text
    # into separate lines.
    args_wrapper = _wrapper(args_width)
    desc_wrapper = _wrapper(desc_width)
    for argument in self._commands + self._options:
      argument["left"] = args_wrapper.wrap(argument["left"])
      argument["right"] = desc_wrapper.wrap(argument["right"])

    # Add command arguments.
    if len(self._commands) > 0:
      commands.append("\nCommands:\n")
      for command in self._commands:
        for idx in range(max(len(command["left"]), len(command["right"]))):
          if idx < len(command["left"]):
            left = command["left"][idx]
          else:
            left = ""
          if idx < len(command["right"]):
            right = command["right"][idx]
          else:
            right = ""
          commands.append(template % (left, right))
          commands.append("\n")

    # Add option arguments.
    if len(self._options) > 0:
      options.append("\nOptions:\n")
      for option in self._options:
        for idx in range(max(len(option["left"]), len(option["right"]))):
          if idx < len(option["left"]):
            left = option["left"][idx]
          else:
            left = ""
          if idx < len(option["right"]):
            right = option["right"][idx]
          else:
            right = ""
          options.append(template % (left, right))
          options.append("\n")

    # Add epilog if provided.
    if "epilog" in self._program and self._program["epilog"] != "" and not \
            str.isspace(self._program["epilog"]):
      epilog.append("\n")
      epilog.extend(epilog_wrapper.wrap(self._program["epilog"]))
      epilog.append("\n")

    return description, commands, options, epilog

  def print_help(self) -> None:
    """Print help to sys.stdout."""
    sys.stdout.write(f"\n{self.format_usage()}\n")
    sys.stdout.write("".join(list(itertools.chain(*self.format_help()))))
    sys.stdout.flush()

  def error(self) -> None:
    """Print hint to stderr and exit."""
    sys.stderr.write(f"\n{self.format_usage()}\n")
    sys.stderr.write("".join(list(itertools.chain(*self.format_help()))))
    sys.exit(1)
