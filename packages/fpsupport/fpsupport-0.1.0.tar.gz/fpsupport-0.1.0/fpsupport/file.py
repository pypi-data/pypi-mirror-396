"""This module wraps file I/O functions in a monad.

fpsupport/file.py Copyright 2025 George Cummings

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing permissions and limitations under the
License.

----

All I/O operations follow the same pattern: they accept an IOType and additional positional and
keyword arguments.

@side_effect: if IOType.ok is cleared (False or None), then the function will return immediately
without changing the IOType data. Otherwise, they execute a function and return a monad.

As Python is not a lazy-evaluation language, this will permit pure functions to test its reaction
to an IO error as a simple boolean without mocking.
"""

from typing import Callable


from .decorator import side_effect
from .monad import Monad
from .struct import IOType


@side_effect
def fopen(io: IOType, *args, **kwargs) -> Monad:  # pylint: disable=unused-argument
    """Open a file and send its results into the IOType.

    Args:
        IOType
        args and kwargs

    Returns:
        Monad(IOType) where IOType.contents holds a file pointer
    """
    return Monad(f_try(open, *args, **kwargs))


def f_try(function: Callable, *args, **kwargs) -> IOType:
    """Helper function that wraps a function with a reaction to an OSError."""
    try:
        return IOType(function(*args, **kwargs), "", True)
    except OSError as e:
        return IOType("", f"{e.filename}: {e.strerror}", False)


@side_effect
def fread(io: IOType, *args, **kwargs) -> Monad:
    """Read a file from a file pointer in a monad.

    Args:
        IOType

    Returns:
        Monad(IOType) where IOType.contents are the results of the file read.
    """
    return Monad(f_try(io.contents.read, *args, **kwargs))
