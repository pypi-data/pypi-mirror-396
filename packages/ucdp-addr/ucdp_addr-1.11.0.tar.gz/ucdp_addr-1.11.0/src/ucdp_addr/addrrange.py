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
Address Range.
"""

import ucdp as u
from icdutil import num
from pydantic import PositiveInt

from .util import calc_depth_size

BASEADDR_DEFAULT = u.Hex(0)


class AddrRange(u.Object):
    """
    Address Range.

    Examples:
        >>> addrrange = AddrRange(size='4k')
        >>> addrrange
        AddrRange(size=Bytesize('4 KB'))
        >>> addrrange.baseaddr
        Hex('0x0')
        >>> addrrange.width
        32
        >>> addrrange.depth
        1024
        >>> addrrange.size
        Bytesize('4 KB')
        >>> addrrange.addrwidth
        12
        >>> addrrange.endaddr
        Hex('0xFFF')
        >>> addrrange.nextaddr
        Hex('0x1000')
        >>> addrrange.wordsize
        4.0
        >>> str(addrrange)
        '0x0 1024x32 (4 KB)'
        >>> str(AddrRange(depth=16))
        '0x0 16x32 (64 bytes)'
        >>> str(AddrRange(size=16))
        '0x0 4x32 (16 bytes)'
    """

    baseaddr: u.Hex = BASEADDR_DEFAULT
    """Base Address"""
    width: PositiveInt = 32
    """Width in Bits."""
    depth: PositiveInt = u.Field(repr=False)
    """Number of words."""
    size: u.Bytes
    """Size in Bytes."""

    def __init__(
        self,
        baseaddr: u.Hex = BASEADDR_DEFAULT,
        width: PositiveInt = 32,
        depth: PositiveInt | None = None,
        size: u.Bytes | None = None,
        **kwargs,
    ):
        depth, size = calc_depth_size(width, depth, size)
        super().__init__(baseaddr=baseaddr, width=width, depth=depth, size=size, **kwargs)

    @property
    def addrwidth(self) -> PositiveInt:
        """Address Width."""
        return num.calc_unsigned_width(int(self.size) - 1)

    @property
    def addrmask(self) -> PositiveInt:
        """Address Width."""
        return (2**self.addrwidth) - 1

    @property
    def endaddr(self) -> u.Hex:
        """End Address - `baseaddr+size-1`."""
        return self.baseaddr + self.size - 1

    @property
    def nextaddr(self) -> u.Hex:
        """Next Free Address - `baseaddr+size`."""
        return self.baseaddr + self.size

    @property
    def wordsize(self) -> float:
        """Number of Bytes Per Word."""
        return self.width / 8

    def __str__(self) -> str:
        return f"{self.baseaddr} {self.org}"

    @property
    def org(self) -> str:
        """Organization."""
        return f"{self.depth}x{self.width} ({self.size})"
