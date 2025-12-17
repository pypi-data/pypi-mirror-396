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
Address Spaces.
"""

from collections.abc import Iterable, Iterator
from logging import getLogger

from .addrspace import Addrspace

LOGGER = getLogger(__name__)

Addrspaces = Iterable[Addrspace]


def join_addrspaces(base: Addrspace, addrspaces: Addrspaces) -> Iterator[Addrspace]:
    """Join Address Spaces."""
    for addrspace in addrspaces:
        joined = base.join(addrspace)
        LOGGER.debug("join_addrspaces: %s+%s=%s", base, addrspace, joined)
        if joined:
            yield joined


def zip_addrspaces(lefts, rights) -> Iterator[tuple[Addrspace, ...]]:
    """
    Zip Address Spaces.

    >>> one = (
    ...     Addrspace(name='a0', baseaddr=0x0000, size=0x1000),
    ...     Addrspace(name='a1', baseaddr=0x1000, size=0x1000))
    >>> other = (
    ...     Addrspace(name='b0', baseaddr=0x0000, size=0x1000),
    ...     Addrspace(name='b1', baseaddr=0x1000, size=0x800),
    ...     Addrspace(name='b2', baseaddr=0x1800, size=0x800))
    >>> for left, right in zip_addrspaces(one, other): print(f"{str(left)!r} {str(right)!r}")
    'a0 +0x0 1024x32' 'b0 +0x0 1024x32'
    'a1 +0x1000 1024x32' 'b1 +0x1000 512x32'
    'a1 +0x1000 1024x32' 'b2 +0x1800 512x32'
    """
    leftiter = iter(lefts)
    rightiter = iter(rights)
    try:
        left = next(leftiter)
        right = next(rightiter)
    except StopIteration:
        pass
    else:
        while True:
            yield left, right
            leftend = left.endaddr <= right.endaddr
            rightend = right.endaddr <= left.endaddr
            if leftend:
                try:
                    left = next(leftiter)
                except StopIteration:
                    break
            if rightend:
                try:
                    right = next(rightiter)
                except StopIteration:
                    break
            assert leftend or rightend
