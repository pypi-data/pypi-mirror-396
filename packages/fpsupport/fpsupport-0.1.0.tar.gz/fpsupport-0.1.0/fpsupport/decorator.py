"""Decorators that are useful for functional programming.

Decorators, of course, are very much part of functional programming as they take functions as an
argument by their very definition.

fpsupport/decorator.py Copyright 2025 George Cummings

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing permissions and limitations under the
License.

"""

import functools
from typing import Callable

from fpsupport import monad


def side_effect(function: Callable) -> Callable:
    r"""Skip a function if the wrapped type's attribute "ok" is None.

    This decorator wraps around functions that accept a Monad that performs IO side-effect like
    system calls, or calls to third-party services. It is used for testing a Python function in the
    same manner that a tail-first functional language is tested.

    - Setting Object.ok to "True" means nothing: the function continues
    - Setting Object.ok to "False" means simulate that the wrapped calls failed somehow, and accept
      the contents of the incoming Monad as the outcome of the function.
    - Setting Object.ok to "None" means simulate that the function succeeded, and accept the
      contents of the incoming Monad as the outcome of the function.

    Example (naive) Usage:

    ```python
    @side_effect
    def my_io(io: IOType) -> Monad:
        file_path = io.contents
        try:
            with open(file_path, "r", encoding="utf-8") as file_pointer:
                return Monad(IOType(file_path.read(), "", True))
        except OSError as e:
            return Monad(IOType("", f"{e.strerror}", False))


    def read_file(io, file_path) -> tuple[int | None, str | None]:
        result = unwrap(Monad(IOType(file_path, io.error_msg, io.ok)))
        if not result.ok:
            return None, None
        return len(result.contents.split("\n")), result.contents


    # Testing: this is what the @side_effect is for. Skip the actual side effect without resorting
    # to Mocking and patching.

    def test_read_file_failure():
        io = Monad(IOType("", "unit test failure", False))
        assert read_file(io, "my_file.txt")[0] == None

    def test_my_io_returns():
        test_data = "Everything is awesome" + "\n" + "When you are part of a team."
        io = Monad(IOType(test_data, "", None)
        assert read_file(io, "my_file.txt") == (2, test_data)
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs) -> monad.Monad:
        struct = args[0]
        if hasattr(struct, "ok"):
            if not struct.ok:
                return monad.Monad(struct)
        return function(*args, **kwargs)

    return wrapper
