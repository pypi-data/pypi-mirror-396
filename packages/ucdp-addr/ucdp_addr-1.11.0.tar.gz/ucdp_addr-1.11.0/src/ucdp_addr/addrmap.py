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
Address Map.
"""

from collections.abc import Callable, Iterator
from typing import TypeAlias

import aligntext
import ucdp as u
from icdutil import num
from ucdp_glbl.attrs import format_attrs

from .addrmapref import AddrMapRef
from .addrspace import Addrspace, ReservedAddrspace
from .addrspaces import Addrspaces
from .defines import Defines

FillAddrspaceFactory: TypeAlias = Callable[[int, int, int], Addrspace]
AddrspaceFilter: TypeAlias = Callable[[Addrspace], bool]


class AddrMap(u.Object):
    """Address Map."""

    unique: bool = False
    fixed_size: u.Bytes | None = None
    defines: Defines = u.Field(default_factory=dict)
    ref: u.TopModRef | None = None

    @staticmethod
    def from_addrspaces(
        addrspaces: Addrspaces,
        unique: bool = False,
        fixed_size: u.Bytes | None = None,
        defines: Defines | None = None,
        ref: u.TopModRef | None = None,
    ) -> "AddrMap":
        """Create From address spaces."""
        addrmap = AddrMap(unique=unique, fixed_size=fixed_size, defines=defines or {}, ref=ref)
        for addrspace in addrspaces:
            addrmap.add(addrspace)
        return addrmap

    _addrspaces: list[Addrspace] = u.PrivateField(default_factory=list)

    def add(self, addrspace: Addrspace) -> None:
        """Add Address Space."""
        self._check_size(addrspace)

        pos = self._find_pos(addrspace)

        if self.unique:
            self._check_overlapping(pos, addrspace)

        self._addrspaces.insert(pos, addrspace)

    def get(self, addrspace: Addrspace) -> AddrMapRef:
        """Add Address Space."""
        for item in self._addrspaces:
            intersect = item.get_intersect(addrspace)
            if intersect:
                return AddrMapRef.create(addrspace=intersect)
        raise ValueError(f"{addrspace!r} does not exists")

    def __iter__(self) -> Iterator[Addrspace]:
        yield from self._addrspaces

    def iter(  # noqa: C901
        self,
        filter_: AddrspaceFilter | None = None,
        fill: FillAddrspaceFactory | bool | None = None,
    ) -> Iterator[Addrspace]:
        """Iterate over Address Spaces."""

        def no_addrspacefilter(_: Addrspace) -> bool:
            return True

        if fill is True:
            fill = create_fill_addrspace

        if not fill:
            if filter_ is None:
                yield from self._addrspaces
            else:
                for addrspace in self._addrspaces:
                    if filter_(addrspace):
                        yield addrspace
        else:
            filter_ = filter_ or no_addrspacefilter
            baseaddr = 0
            idx = 0
            for addrspace in self._addrspaces:
                if not filter_(addrspace):
                    continue

                # fill before
                if addrspace.baseaddr > baseaddr:
                    yield fill(idx, baseaddr, addrspace.baseaddr - baseaddr)
                    idx += 1

                # element
                yield addrspace
                baseaddr = addrspace.nextaddr

            if self.addrwidth:
                nextaddr = 2**self.addrwidth

                # fill end
                if nextaddr > baseaddr:
                    yield fill(idx, baseaddr, nextaddr - baseaddr)

    @property
    def size(self) -> u.Bytes | None:
        """
        Size in Bytes.
        """
        size = self.fixed_size
        if size is None:
            lastaddr = self.lastaddr
            if lastaddr is None:
                return None
            size = u.Bytesize(lastaddr + 1)
        return size

    @property
    def addrwidth(self) -> int | None:
        """
        Address Width.
        """
        size = self.size
        if size is None:
            return None
        return num.calc_unsigned_width(int(size - 1))

    @property
    def firstaddr(self) -> int | None:
        """
        First used address.
        """
        try:
            return self._addrspaces[0].baseaddr
        except IndexError:
            return None

    @property
    def lastaddr(self) -> int | None:
        """
        Last used address.
        """
        try:
            return self._addrspaces[-1].endaddr
        except IndexError:
            return None

    @property
    def addrslice(self) -> u.Slice | None:
        """
        Address Slice.
        """
        addrspaces = self._addrspaces
        addrwidth = self.addrwidth
        if addrwidth is None or not addrspaces:
            return None

        minsize = int(min(addrspace.size for addrspace in addrspaces))

        # Ensure at least one address decoding bit
        if minsize == self.size:
            left = addrwidth
        else:
            left = addrwidth - 1

        right = min(num.calc_lowest_bit_set(minsize), left)
        return u.Slice(left=left, right=right)

    def get_free_baseaddr(self, size: u.Bytes, align=None, start=None) -> int:
        """
        Return baseaddress of free window with `size`.

        Args:
            size: Window Size

        Keyword Args:
            align: Alignment, default aligned to size
            start: Start search behind given address
        """
        size = u.Bytesize(size)
        if align is None:
            align = size
        if start is None:
            lastaddr = self.lastaddr
            start = lastaddr + 1 if lastaddr else 0

        baseaddr = u.Hex(self._find_space(size, align, start))

        # End Check
        endaddr = baseaddr + size
        size = self.fixed_size
        if size is not None:
            if endaddr >= size:
                size_hex = u.Hex(size)
                raise ValueError(f"End address {endaddr} would exceed maximum size {size_hex} ({size})")

        return baseaddr

    def _find_space(self, size, align, start):
        addr = start = num.align(start, align=align)
        for item in self._addrspaces:
            if item.endaddr < start:
                # skip all before start
                addr = max(num.align(item.nextaddr, align=align), addr)
                continue
            if item.baseaddr >= (addr + size):
                break
            addr = num.align(item.nextaddr, align=align)
        return addr

    def get_overview(self, minimal: bool = False, fill: FillAddrspaceFactory | bool | None = None) -> str:
        """
        Return overview table.
        """

        def align(data) -> str:
            lines = list(data)
            lens = (max(len(cell) for cell in row) for row in zip(*lines, strict=False))
            lines.insert(1, ("-" * len_ for len_ in lens))
            return aligntext.align(lines, seps=(" | ",), sepfirst="| ", seplast=" |") + "\n"

        defines = ", ".join(f"{define}={value!r}" for define, value in self.defines.items()) or None
        header = [
            f"* Top:     `{self.ref}`",
            f"* Defines: `{defines}`",
            f"* Size:    `{self.size}`",
        ]
        parts = [
            "\n".join(header),
            align(self.get_addrspaces_overview(fill=fill)),
        ]
        if not minimal:
            parts.append(align(self.get_word_fields_overview()))
        return "\n\n".join(parts)

    def get_addrspaces_overview(
        self, fill: FillAddrspaceFactory | bool | None = None
    ) -> Iterator[tuple[str, str, str, str, str]]:
        """Get Address Spaces Overview Data."""
        yield ("Addrspace", "Type", "Base", "Size", "Infos", "Attributes")
        for addrspace in self.iter(fill=fill):
            classname = addrspace.__class__.__name__.replace("Addrspace", "") or "-"
            infos = []
            if addrspace.is_sub:
                infos.append("Sub")
            if addrspace.is_volatile:
                infos.append("Volatile")
            yield (
                addrspace.name,
                classname,
                f"`{addrspace.base}`",
                f"`{addrspace.org}`",
                ",".join(infos),
                format_attrs(addrspace.attrs),
            )

    def get_word_fields_overview(  # noqa: C901
        self, addrspaces: bool = True, words: bool = True, fields: bool = True
    ) -> Iterator[tuple[str, str, str, str, str, str, str]]:
        """Get Word-Fields Overview Data."""
        yield ("Addrspace", "Word", "Field", "Offset", "Access", "Reset", "Infos", "Attributes")
        resolver = u.ExprResolver()
        for addrspace in self:
            # address spaces
            if addrspaces:
                infos = []
                if addrspace.is_volatile:
                    infos.append("Volatile")
                yield (
                    addrspace.name,
                    "",
                    "",
                    f"`{addrspace.base}`",
                    addrspace.access,
                    "",
                    ",".join(infos),
                    format_attrs(addrspace.attrs),
                )
            # words
            for word in addrspace.words:
                if words:
                    infos = []
                    if word.is_volatile:
                        infos.append("Volatile")
                    yield (
                        addrspace.name,
                        word.name,
                        "",
                        f"`  +{word.slice}`",
                        word.access,
                        "",
                        ",".join(infos),
                        format_attrs(word.attrs),
                    )
                # fields
                if fields:
                    for field in word.fields:
                        infos = []
                        if field.is_volatile:
                            infos.append("Volatile")
                        if field.is_const:
                            infos.append("CONST")
                        reset = resolver.resolve_value(field.type_)
                        yield (
                            addrspace.name,
                            word.name,
                            field.name,
                            f"`    [{field.slice}]`",
                            str(field.access),
                            f"`{reset}`",
                            ",".join(infos),
                            format_attrs(field.attrs),
                        )

    def _check_size(self, addrspace: Addrspace) -> None:
        fixed_size = self.fixed_size
        if fixed_size is not None:
            if addrspace.endaddr >= fixed_size:
                raise ValueError(f"{addrspace!r}: exceeds maximum size: {fixed_size}.")

    def _find_pos(self, addrspace: Addrspace) -> int:
        baseaddr = addrspace.baseaddr
        for pos, item in enumerate(self._addrspaces):
            if item.baseaddr > baseaddr:
                return pos
        return len(self._addrspaces)

    def _check_overlapping(self, pos: int, addrspace: Addrspace) -> None:
        addrspaces = self._addrspaces
        # lower
        try:
            lower = addrspaces[pos - 1]
        except IndexError:
            pass
        else:
            if addrspace.is_overlapping(lower):
                raise ValueError(f"{addrspace!r} overlaps with {lower!r}")
        # upper
        try:
            upper = addrspaces[pos]
        except IndexError:
            pass
        else:
            if addrspace.is_overlapping(upper):
                raise ValueError(f"{addrspace!r} overlaps with {upper!r}")


def create_fill_addrspace(idx, baseaddr, size) -> Addrspace:
    """Create Fill Addrspace."""
    return ReservedAddrspace(name=f"reserved{idx}", baseaddr=baseaddr, size=size, is_sub=False)
