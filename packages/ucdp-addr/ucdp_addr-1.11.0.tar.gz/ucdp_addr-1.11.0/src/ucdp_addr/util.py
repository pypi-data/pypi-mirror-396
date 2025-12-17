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

"""
Utilities.
"""

import ucdp as u
from humannum import bytesize_


def calc_depth_size(width: int, depth: int | None = None, size: u.Bytes | None = None) -> tuple[int, u.Bytes]:
    """
    Calc Either Depth Or Size.

    >>> calc_depth_size(32, depth=64)
    (64, Bytesize('256 bytes'))
    >>> calc_depth_size(32, size='64')
    (16, Bytesize('64 bytes'))
    >>> calc_depth_size(32, depth=64, size=256)
    (64, Bytesize('256 bytes'))
    >>> calc_depth_size(32)
    Traceback (most recent call last):
        ...
    ValueError: Either 'depth' or 'size' are required.
    >>> calc_depth_size(32, depth=64, size='64')
    Traceback (most recent call last):
        ...
    ValueError: 'depth' and 'size' are mutually exclusive.
    """
    # Provide either 'size' or 'depth' and calculate the other
    if size is None:
        if depth is None:
            raise ValueError("Either 'depth' or 'size' are required.")
        size = bytesize_((width * depth) // 8)
    else:
        size = bytesize_(size)
        depth_calculated = int(size * 8 // width)
        if depth is not None and depth != depth_calculated:
            raise ValueError("'depth' and 'size' are mutually exclusive.")
        depth = depth_calculated
    return depth, size


def split_keyvaluepairs(value: str) -> dict[str, str]:
    """
    Split comma-separated fields into (name, value) pairs.

    >>> split_keyvaluepairs('a=4')
    {'a': '4'}
    >>> split_keyvaluepairs('a=4, b=a')
    {'a': '4', 'b': 'a'}
    >>> split_keyvaluepairs('a=4, b')
    Traceback (most recent call last):
      ...
    ValueError: Invalid key=value pair: 'b'
    >>> split_keyvaluepairs('a=4, a=a')
    Traceback (most recent call last):
      ...
    ValueError: Duplicate key 'a'
    """
    data = {}
    for pair in value.split(","):
        pair = pair.strip()  # noqa: PLW2901
        if "=" not in pair:
            raise ValueError(f"Invalid key=value pair: '{pair}'")
        fname, fvalue = pair.split("=", 1)
        if fname not in data:
            data[fname] = fvalue
        else:
            raise ValueError(f"Duplicate key {fname!r}")
    return data
