"""Structures that can be passed into base monads.

fpsupport/struct.py Copyright 2025 George Cummings

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing permissions and limitations under the
License.
"""

from typing import Any
from dataclasses import dataclass


@dataclass
class IOType:
    """A type used in a Monad to capture IO side effects: outcome, errors, and error messages.

    IOType.outcome is the testable, provable results of an IO call, failure or success.
    IOType.error_msg is meta-information about why a call failed.
    IOType.ok is the meta-information on whether the call passed, failed, or was skipped in a test.
    """

    def __init__(self, outcome: Any = None, error_msg: str | None = None, ok: bool | None = True):
        """Initialize IOType, ensuring values are of type."""
        self.outcome: Any = outcome
        if not isinstance(error_msg, str | None):
            raise TypeError("IOType attribute 'error_msg' must be of type str or None")

        self.error_msg: str | None = error_msg

        if not isinstance(ok, bool | None):
            raise TypeError("IOType attribute 'ok' must be of type bool or None")
        self.ok: bool | None = ok
