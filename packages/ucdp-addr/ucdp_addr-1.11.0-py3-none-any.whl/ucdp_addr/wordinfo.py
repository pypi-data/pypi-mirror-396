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
Word Information.

"""

from collections.abc import Iterator
from typing import TypeAlias

import ucdp as u
from pydantic import PositiveInt

from .access import is_read_repeatable, is_write_repeatable
from .addrinfo import _apply_offset
from .addrmap import AddrMap
from .addrmapref import AddrMapRef, ToAddrMapRef
from .addrrange import AddrRange
from .addrspace import Word, read_on_modify, resolve_field_value
from .data import Data, DataType, get_datatype, get_size
from .datainfo import AddrData, _iter_data
from .resolver import resolve
from .util import split_keyvaluepairs

Offset: TypeAlias = PositiveInt
Size: TypeAlias = PositiveInt
Depth: TypeAlias = PositiveInt
FieldValues: TypeAlias = dict[str, str | int]


class WordInfo(u.Object):
    """WordInfo Info."""

    ref: AddrMapRef
    """Address Map Reference."""
    addrrange: AddrRange
    """Accessed Address Range."""
    datatype: DataType
    """Data Type."""
    data: Data
    """Data."""
    mask: u.Hex | None = None
    """Data Masking."""
    rmw: bool | None = None
    """Read Modify Write - Read before write required."""
    read_repeatable: bool | None = None
    """Read Operation Has No Side-Effects."""
    write_repeatable: bool | None = None
    """Write Operation Has No Side-Effects."""

    def __str__(self):
        info = f"{self.ref!s} [{self.addrrange!s}]"
        if self.mask is not None:
            info = f"{info} mask={self.mask}"
        if self.rmw:
            info = f"{info} RMW"
        if self.read_repeatable is False:
            info = f"{info} !R"
        if self.write_repeatable is False:
            info = f"{info} !W"
        return f"{info} {self.datatype.name}: {self.data}"

    @staticmethod
    def create(
        addrmap: AddrMap,
        item: ToAddrMapRef,
        data: Data | str | FieldValues,
        offset: Offset | None = None,
        mask: int | None = None,
        wordsize: Size | None = None,
    ) -> "WordInfo":
        """
        Create `WordInfo`.

        Args:
            addrmap: Address Map
            item: Thing to be resolved
            data: Data

        Keyword Args:
            offset: address offset in bytes
            mask: Mask for non-field access.
            wordsize: Size of one word in bytes (Only allowed if `item` is an `int`)
        """
        # determine size from data on raw integer address
        if isinstance(item, int):
            item = AddrRange(baseaddr=item + (offset or 0), size=get_size(data, wordsize=wordsize or 4))
            offset = None
        elif wordsize is not None:
            raise ValueError("'wordsize' is forbidden for non integer.")

        ref = resolve(addrmap, item)
        addrrange = ref.addrrange

        # apply offset
        if offset is not None:
            addrrange = _apply_offset(ref, addrrange, offset)

        if ref.word:
            if ref.field:
                # field
                if mask is not None:
                    raise ValueError("'mask' is not allowed for fields")
                if not isinstance(data, (int, str)):
                    raise TypeError(f"'data' must be 'int' or 'str' for fields, not {data}")
                slice_ = ref.field.slice
                data = slice_.update(0, resolve_field_value(ref.field, data))
                mask = slice_.mask
            else:
                # word
                if not isinstance(data, (int, str, dict)):
                    raise TypeError(f"'data' must be 'int', 'str' or 'dict' for fields, not {data}")
                data, mask = _resolve_word(ref.word, data, mask)
        else:
            # address
            datatype = get_datatype(data)
            addrrange = _strip_size(data, datatype, addrrange)  # type: ignore[arg-type]
            return WordInfo(
                ref=ref,
                datatype=datatype,
                addrrange=addrrange,
                data=data,
                mask=mask,
            )
        accesses = [field.bus for field in ref.word.fields if field.bus]
        return WordInfo(
            ref=ref,
            addrrange=addrrange,
            data=data,
            datatype=DataType.SINGLE,
            mask=mask,
            rmw=read_on_modify(ref.word, mask) if mask is not None else False,
            read_repeatable=is_read_repeatable(accesses),
            write_repeatable=is_write_repeatable(accesses),
        )

    def iter(self) -> Iterator[AddrData]:
        """Iteratate over single address value pairs according to access."""
        yield from _iter_data(self.datatype, self.data, self.addrrange)

    def addrs(self) -> Iterator[int]:
        """Addresses."""
        for addr, _ in _iter_data(self.datatype, self.data, self.addrrange):
            yield addr


def _strip_size(data: Data, datatype: DataType, addrrange: AddrRange) -> AddrRange:
    if datatype == DataType.SINGLE:
        size = addrrange.wordsize
    elif datatype == DataType.BURST:
        size = int(addrrange.wordsize * len(data))  # type: ignore[operator,arg-type]
    else:
        addrs = [addr for addr, _ in data]  # type:ignore[union-attr]
        size = max(addrs) + addrrange.wordsize

    if size > addrrange.size:
        raise ValueError(f"data size {size!r} exceeds size ({addrrange.size})")
    return addrrange.new(size=size, depth=None)


def _resolve_word(word: Word, data: str | int | FieldValues, mask: int | None) -> tuple[int, int | None]:
    if isinstance(data, int):
        return data, mask

    # str ==> dict
    if isinstance(data, str):
        values = split_keyvaluepairs(data)
    else:
        values = dict(data)  # type: ignore[arg-type]

    # Default
    default = values.pop("*", None)
    if default:
        for field in word.fields:
            if field.name not in values:
                values[field.name] = resolve_field_value(field, default)  # type: ignore[assignment]

    # Evaluate Fields
    result, mask = 0, 0
    for field in word.fields:
        try:
            rawvalue = values.pop(field.name)
        except KeyError:
            continue
        value = resolve_field_value(field, rawvalue)
        slice_ = field.slice
        result = slice_.update(result, value, is_signed=u.is_signed(field.type_))
        mask |= slice_.mask

    # Unknown ones
    if values:
        fieldnames = ", ".join(repr(value) for value in values)
        raise ValueError(f"Unknown field names: {fieldnames}")
    return result, mask
