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
Address Information.

Access can be done to addrspaces, words, fields
and addresses in a single, burst or scatter flavour using offsets, masks, etc.
`create` takes all these variants into account and serves a normalized information set as `AddrInfo`.
"""

from collections.abc import Iterator
from typing import TypeAlias

import ucdp as u
from pydantic import PositiveInt

from .addrmap import AddrMap
from .addrmapref import AddrMapRef, ToAddrMapRef
from .addrrange import AddrRange
from .resolver import resolve

Size: TypeAlias = PositiveInt
Depth: TypeAlias = PositiveInt


class AddrInfo(u.Object):
    """Address Info."""

    ref: AddrMapRef
    addrrange: AddrRange
    mask: u.Hex | None = None

    def __str__(self) -> str:
        info = f"{self.ref!s} [{self.addrrange!s}]"
        if self.mask is not None:
            info = f"{info} mask={self.mask}"
        return info

    @staticmethod
    def create(addrmap: AddrMap, item: ToAddrMapRef, offset: int | None = None, mask: int | None = None) -> "AddrInfo":
        """
        Create `AddrInfo`.

        Args:
            addrmap: Address Map
            item: Thing to be resolved

        Keyword Args:
            offset: address offset in bytes
            mask: Value Mask (not allowed for fields)

        Example Address Map:

            >>> import ucdp as u
            >>> from ucdp_addr import Addrspace, Word, Field, AddrMap
            >>> addrmap = AddrMap()
            >>> for idx, aname in enumerate(("uart", "spi", "owi")):
            ...     addrspace = Addrspace(name=aname, width=32, depth=8, baseaddr=8*4*idx)
            ...     addrmap.add(addrspace)
            ...     word = addrspace.add_word("ctrl")
            ...     field = word.add_field("ena", u.BitType(), "RW")
            ...     word = addrspace.add_word("stat")
            ...     field = word.add_field("bsy", u.BitType(), "RO", offset=9)

        Addrspace:

            >>> addrinfo = AddrInfo.create(addrmap, "spi")
            >>> str(addrinfo)
            'spi [0x20 8x32 (32 bytes)]'
            >>> addrinfo.ref
            AddrMapRef(..., addrspace=Addrspace(name='spi', baseaddr=Hex('0x20'), size=Bytesize('32 bytes')))
            >>> addrinfo.mask
            >>> tuple(addrinfo.iter())
            (Hex('0x20'), Hex('0x24'), Hex('0x28'), Hex('0x2C'), Hex('0x30'), Hex('0x34'), Hex('0x38'), Hex('0x3C'))

            >>> addrinfo = AddrInfo.create(addrmap, "spi", offset=8, mask=0xF0)
            >>> str(addrinfo)
            'spi [0x28 6x32 (24 bytes)] mask=0xF0'
            >>> addrinfo.mask
            Hex('0xF0')
            >>> tuple(addrinfo.iter())
            (Hex('0x28'), Hex('0x2C'), Hex('0x30'), Hex('0x34'), Hex('0x38'), Hex('0x3C'))

        Word:

            >>> addrinfo = AddrInfo.create(addrmap, "spi.stat")
            >>> str(addrinfo)
            'spi.stat [0x24 1x32 (4 bytes)]'
            >>> addrinfo.ref
            AddrMapRef(..., addrspace=Addrspace(name='spi', baseaddr=Hex('0x20'), ..., word=Word(name='stat', ...)
            >>> addrinfo.mask
            >>> tuple(addrinfo.iter())
            (Hex('0x24'),)

            >>> AddrInfo.create(addrmap, "spi.stat", offset=8)
            Traceback (most recent call last):
              ...
            ValueError: 'offset' is not allowed for words and fields

        Field:

            >>> addrinfo = AddrInfo.create(addrmap, "spi.stat.bsy")
            >>> str(addrinfo)
            'spi.stat.bsy [0x24 1x32 (4 bytes)] mask=0x200'
            >>> addrinfo.ref
            AddrMapRef(...Hex('0x20'), ... word=Word(name='stat', ...(name='bsy', type_=BitType(), bus=RO, offset=9))
            >>> addrinfo.mask
            Hex('0x200')
            >>> tuple(addrinfo.iter())
            (Hex('0x24'),)

            >>> AddrInfo.create(addrmap, "spi.stat.bsy", offset=8)
            Traceback (most recent call last):
              ...
            ValueError: 'offset' is not allowed for words and fields
            >>> AddrInfo.create(addrmap, "spi.stat.bsy", mask=8)
            Traceback (most recent call last):
              ...
            ValueError: 'mask' is not allowed for fields
        """
        ref = resolve(addrmap, item)
        addrrange = ref.addrrange
        if ref.field:
            if mask is not None:
                raise ValueError("'mask' is not allowed for fields")
            mask = ref.field.slice.mask

        # apply offset
        if offset is not None:
            addrrange = _apply_offset(ref, addrrange, offset)

        return AddrInfo(ref=ref, addrrange=addrrange, mask=mask)

    def iter(self) -> Iterator[u.Hex]:
        """Iteratate over address ranges."""
        addrrange = self.addrrange
        wordsize = addrrange.wordsize
        for idx in range(addrrange.depth):
            yield addrrange.baseaddr + int(idx * wordsize)


def _apply_offset(ref: AddrMapRef, addrrange: AddrRange, offset: int) -> AddrRange:
    if ref.word or ref.field:
        raise ValueError("'offset' is not allowed for words and fields")
    if offset >= addrrange.size:
        raise ValueError(f"offset={offset!r} exceeds size ({addrrange.size})")
    return addrrange.new(baseaddr=addrrange.baseaddr + offset, size=addrrange.size - offset, depth=None)
