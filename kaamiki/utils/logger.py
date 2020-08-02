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

"""Utility for logging all Kaamiki events."""

import getpass
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Tuple

USER = getpass.getuser().lower().replace(" ", "-")


class Neo(type):
    """
    A naive implementation of Singleton design pattern.

    Singleton is a creational design pattern, which ensures that
    only one object of its kind exists and provides a single point
    of access to it for any other code.

    The below is a non thread-safe implementation of a Singleton.

    See https://stackoverflow.com/q/6760685 for more methods of
    implementing singletons in code.

    You can instantiate YourClass multiple times yet you would get
    reference to same object:

    >>> class YourClass(metaclass=Neo):
    ...     pass

    >>> singleton_obj1 = YourClass()
    >>> singleton_obj2 = YourClass()
    >>> singleton_obj1
    <__main__.YourClass object at 0x7fc8f1948970>
    >>> singleton_obj2
    <__main__.YourClass object at 0x7fc8f1948970>
    """
    # See https://refactoring.guru/design-patterns/singleton/python/example
    # for a thread-safe implementation.
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class LogFormatter(logging.Formatter, metaclass=Neo):
    """
    Formatting logs gracefully.

    As name suggests, LogFormatter is a formatter class for
    formatting logs across various log levels. It implements a
    clean & uniform way of logging records across all logging
    levels including exceptions.
    """

    def __init__(self) -> None:
        """Instantiate class."""
        self._timestamp_format = "%a %b %d, %Y %H:%M:%S"
        self._log_format = ("%(asctime)s.%(msecs)03d %(levelname)8s "
                            "[%(process)07d] {:>28}:%(lineno)04d %(message)s")
        self._exc_format = "{0} caused due to {1} in {2}() on line {3}."

    def formatException(self, exc_info: Tuple[Any, ...]) -> str:
        """Format traceback message into string representation."""
        return repr(super().formatException(exc_info))

    def format(self, record: logging.LogRecord) -> str:
        """Format output log message."""
        # Shorten longer module names with an ellipsis while logging.
        # This will ensure that the module names stay consistent
        # throughout the logs.
        module = os.path.relpath(record.pathname).replace("/" or "\\", ".")

        if len(module[:-3]) < 25:
            module = module
        else:
            module = module[:25] + bool(module[25:]) * "..."

        formatted = logging.Formatter(self._log_format.format(module),
                                      self._timestamp_format).format(record)

        if record.exc_text:
            exc_msg = self._exc_format.format(
                record.exc_info[1].__class__.__name__,
                str(record.msg).lower(),
                record.funcName,
                record.exc_info[2].tb_lineno)
            raw = formatted.replace("\n", "")
            raw = raw.replace(str(record.exc_info[-2]), exc_msg)
            formatted, _, _ = raw.partition("Traceback")

        return formatted


class StreamFormatter(logging.StreamHandler, metaclass=Neo):
    """
    Stream logs on terminal with singleton backend.

    StreamFormatter is a traditional logging stream handler with
    taste of Singleton design pattern.
    """

    def __init__(self) -> None:
        """Instantiate class."""
        super().__init__(sys.stdout)


class ArchiveHandler(RotatingFileHandler, metaclass=Neo):
    """
    Backup logs which grow bigger in size.

    ArchiveHandler is a rotating file handler class which
    creates an archive of the log to rollover once it reaches a
    predetermined size. When the log is about to be exceed the set
    size, the file is closed and a new log is silently opened for
    logging.

    This class ensures that the file won't grow indefinitely.
    """

    def __init__(self,
                 name: str,
                 mode: str = "a",
                 size: int = 0,
                 backups: int = 0,
                 encoding: str = None,
                 delay: bool = False) -> None:
        """
        Instantiate class.

        Args:
            name: Name of the log file.
            mode: Log file writing mode.
            size: Maximum file size limit for backup.
            backups: Total number of backup.
            encoding: File encoding.
            delay: Delay for backup.
        """
        self._count = 0
        super().__init__(filename=name,
                         mode=mode,
                         maxBytes=size,
                         backupCount=backups,
                         encoding=encoding,
                         delay=delay)

    def doRollover(self) -> None:
        """Does a rollover."""
        if self.stream:
            self.stream.close()

        if not self.delay:
            self.stream = self._open()

        self._count += 1
        self.rotate(self.baseFilename, f"{self.baseFilename}.{self._count}")


class SilenceOfTheLogs(object):
    """
    Log all Kaamiki events silently.

    SilenceOfTheLogs is a custom logger which records Kaamiki events
    silently. This logger is equipped with Rotating file handler and
    a custom Log formatter which enables sequential archiving and
    clean log formatting.
    """

    def __init__(self,
                 name: str = None,
                 level: str = "debug",
                 size: int = None,
                 backups: int = None) -> None:
        """
        Instantiate class.

        Args:
            name: Name for log file.
            level: Default logging level to log messages.
            size: Maximum file size limit for backup.
            backups: Total number of backup.
        """
        try:
            self._temp = os.path.abspath(sys.modules["__main__"].__file__)
        except AttributeError:
            self._temp = "kaamiki.py"

        self._name = name.lower() if name else Path(self._temp.lower()).stem
        self._name = self._name.replace(" ", "-")
        self._level = level.upper()
        self._size = int(size) if size else 1000000
        self._backups = int(backups) if backups else 0
        self._logger = logging.getLogger()
        self._logger.setLevel(self._level)

        self._path = os.path.expanduser(f"~/.kaamiki/{USER}/logs/")

        if not os.path.exists(self._path):
            os.makedirs(self._path)

        self._file = os.path.join(self._path, "".join([self._name, ".log"]))
        self._formatter = LogFormatter()

    @property
    def log(self) -> logging.Logger:
        """Log Kaamiki events."""
        # Archive the logs once their file size reaches 1 Mb.
        # See ArchiveHandler() for more information. You can change
        # the way archived logs are named using ArchiveHandler().
        file_handler = ArchiveHandler(self._file,
                                      size=self._size,
                                      backups=self._backups)
        file_handler.setFormatter(self._formatter)
        self._logger.addHandler(file_handler)
        # Stream Handler will print duplicate logs if the same instance
        # of the log object is called multiple times. Unlike file
        # handler, stream handler doesn't support Singleton pattern.
        stream_handler = StreamFormatter()
        stream_handler.setFormatter(self._formatter)
        self._logger.addHandler(stream_handler)
        return self._logger
