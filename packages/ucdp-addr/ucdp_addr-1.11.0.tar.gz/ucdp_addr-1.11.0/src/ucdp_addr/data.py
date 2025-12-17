#
# MIT License
#
# Copyright (c) 2024-2025 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Access Type Description."""

from enum import Enum
from typing import Any, TypeAlias

Data: TypeAlias = int | tuple[int, ...] | list[int] | tuple[tuple[int, int], ...] | list[tuple[int, int]]
"""Data."""


class DataType(Enum):
    """Trans Type."""

    SINGLE = 0
    BURST = 1
    SCAT = 2

    def __repr__(self):
        return self.name


def check_data(data: Data, width: int):
    """Check Data."""
    high = 2**width - 1
    for idx, value in enumerate(_unify_data(data)):
        if value > high or value < 0:
            raise ValueError(f"value {value} at index {idx} exceeds limits [0, {high}]")


def _unify_data(data: Data) -> list[int]:
    if isinstance(data, int):
        return [data]
    if isinstance(data, (tuple, list)):
        if any(isinstance(item, int) for item in data):
            return data  # type: ignore[return-value]
        if any(isinstance(item, tuple) and len(item) == 2 for item in data):  # noqa: PLR2004
            return [value for _, value in data]
    raise TypeError(data)


def get_size(data: Any, wordsize: int) -> int:
    """Determine Maximum Addressed Size of Data."""
    if isinstance(data, int):
        return wordsize
    if isinstance(data, (tuple, list)):
        if any(isinstance(item, int) for item in data):
            return wordsize * len(data)
        if any(isinstance(item, tuple) and len(item) == 2 for item in data):  # noqa: PLR2004
            addrs = [addr for addr, _ in data]  # type:ignore[union-attr]
            return max(addrs) + wordsize
    raise TypeError(data)


def get_datatype(data: Any) -> DataType:
    """Data Type."""
    if isinstance(data, int):
        return DataType.SINGLE
    if isinstance(data, (tuple, list)):
        if any(isinstance(item, int) for item in data):
            return DataType.BURST
        if any(isinstance(item, tuple) and len(item) == 2 for item in data):  # noqa: PLR2004
            return DataType.SCAT
    raise TypeError(data)
