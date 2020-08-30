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

"""Utility of common tools."""

import os
import socket
from datetime import datetime
from glob import glob
from typing import Any, Sequence, Union

from kaamiki.utils.logger import Neo, SilenceOfTheLogs

log = SilenceOfTheLogs().log


class CSVDataWriter(object, metaclass=Neo):
  """
  A singleton rotating CSV file writer.

  As the name speaks for itself, `CSVDataWriter` is a csv writer
  class which exercises singleton design pattern. By inheriting
  singleton design, we are able to initialise only one instance
  of this class for all csv writing operations.
  The class implements a mechanism like rotating file handlers
  which rotates csv files once they reach a certain size.
  """

  def __init__(self,
               path: str,
               mode: str = "a",
               encoding: str = "utf-8",
               delimiter: str = ",",
               size: int = 100000) -> None:  # 1 MB
    """Instantiate class."""
    # See https://stackoverflow.com/a/10896813 for more help.
    self._path = path
    self._mode = mode
    self._encoding = encoding
    self._delimiter = delimiter
    self._size = size
    # For accessing the last `numbered` file in a directory
    # using glob see https://stackoverflow.com/a/17985613.
    self._files = sorted(glob(f"{self._path[:-4]}*.csv"), reverse=True)

    if self._files:
      self._count = int(os.path.basename(self._files[0][-7:-4]))
    else:
      self._count = 1

    self._open()
    self._rotate()

  @property
  def _filename(self) -> str:
    """Return rotated CSV filename constructor."""
    return f"{self._path[:-4]}-{self._count:>03}.csv"

  def _open(self) -> None:
    """Open CSV file for writing."""
    self.handler = open(self._filename, self._mode, encoding=self._encoding)

  def _close(self) -> None:
    """Close CSV file."""
    self.handler.close()

  def _rotate(self) -> None:
    """Rotates file once it reaches a particular size."""
    if os.path.getsize(self._filename) > self._size:
      log.debug("Rotating csv file...")
      self._close()
      self._count += 1
      self._open()

  def write(self, headers: Sequence[Any], *args: Sequence[Any]) -> None:
    """Write data to a CSV file."""
    # This ensure that the headers are written only once.
    if os.path.getsize(self._filename) == 0:
      self.handler.write(self._delimiter.join(headers) + "\n")
    # pyright: reportGeneralTypeIssues=false
    args = list(map(lambda xa: "" if xa is None else str(xa), args))
    self.handler.write(self._delimiter.join(args) + "\n")
    self.handler.flush()
    self._rotate()


def connected(host: str = "8.8.8.8",
              port: int = 53,
              timeout: float = 10.0) -> bool:
  """
  Return the status of network connection via built-in sockets.
  It is a non-threaded implementation for checking the network.

  Args:
    host: Host IP address or Hostname of a webserver.
    port: Port of the webserver.
    timeout: Request timeout.

  Note:
    `8.8.8.8` or `google-public-dns-a.google.com` is public DNS
    for Google which is accessible via TCP port 53.
  """
  # TODO(xames3): Build a thread-safe implementation for this function.
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    log.debug("Connection established with the host.")
    return True
  except socket.error:
    log.error("Connection refused, the host is unreachable.")
    return False


# NOTE(xames3): If anybody wants to use now() as lambda function,
# see this: now = lambda: datetime.now().replace(microsecond=0)
def now() -> datetime:
  """Return current time without microseconds."""
  return datetime.now().replace(microsecond=0)


def seconds_to_datetime(seconds: Union[float, int]) -> str:
  """Convert seconds to datetime string."""
  minutes, seconds = divmod(int(seconds), 60)
  hours, minutes = divmod(minutes, 60)
  days, hours = divmod(hours, 24)
  return f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"
