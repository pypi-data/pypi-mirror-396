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

"""Module, Word and Field Reference."""

from typing import TypeAlias

import ucdp as u

from .addrrange import AddrRange
from .addrspace import Addrspace, Field, Word


class AddrMapRef(u.Object):
    """Address Map Reference."""

    addrrange: AddrRange
    """Address Range."""

    addrspace: Addrspace | None = None
    """Address Space."""

    word: Word | None = None
    """Word."""

    field: Field | None = None
    """Field."""

    def __str__(self) -> str:
        if self.addrspace:
            result = f"{self.addrspace.name}"
            if self.word:
                result = f"{result}.{self.word.name}"
                if self.field:
                    result = f"{result}.{self.field.name}"
            return result
        return f"{self.addrrange.baseaddr}"

    @staticmethod
    def create(
        addrspace: Addrspace, word: Word | None = None, field: Field | None = None, addrrange: AddrRange | None = None
    ) -> "AddrMapRef":
        """
        Create Addrspace with Proper AddrRange.

        Args:
            addrspace: Address Space

        Keyword Args:
            word: Word
            field: Field (requires word as well)
            addrrange: Address Range
        """
        if addrrange is None:
            if word:
                addrrange = AddrRange(
                    baseaddr=addrspace.baseaddr + word.byteoffset,
                    width=word.width,
                    depth=word.depth or 1,
                )
            else:
                addrrange = AddrRange(baseaddr=addrspace.baseaddr, width=addrspace.width, depth=addrspace.depth)
        return AddrMapRef(addrrange=addrrange, addrspace=addrspace, word=word, field=field)


ToAddrMapRef: TypeAlias = AddrMapRef | AddrRange | Addrspace | str | int
"""Unresolved Address Map Reference."""

RawAddrMapRef = ToAddrMapRef
"""Obsolete Alias."""
