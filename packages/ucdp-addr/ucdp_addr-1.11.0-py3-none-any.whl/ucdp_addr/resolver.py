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

"""Module, Word and Field Resolver."""

import re
from collections.abc import Iterator

from matchor import match

from .addrmap import AddrMap
from .addrmapref import AddrMapRef, ToAddrMapRef
from .addrrange import AddrRange
from .addrspace import Addrspace, Word

_RE_RESOLVE = re.compile(
    r"\A(?P<apat>[A-Za-z\*\?][A-Za-z0-9_\*\?]*)"
    r"(\.(?P<wpat>[A-Za-z\*\?][A-Za-z0-9_\*\?]*)"
    r"(\.(?P<fpat>[A-Za-z][A-Za-z0-9_\*\?]*))?)?\Z"
)


def resolve(addrmap: AddrMap, item: ToAddrMapRef) -> AddrMapRef:
    """
    Retrieve AddrSpace, Word and Field referenced by `item` from `addrmap`.

    `item` may be a string pattern with word and field name separated by '.' according to this scheme:
    'addrspace[.word[.field]]'. Wildcards '*' and '?' are supported. The first match is returned.

    `item` may be an address (integer). On `check=True` the address is checked to be covered by a valid
    addrspace and word, if the addrspace contains words.

    `item` may be already a address map reference. On `check=True` the address is checked to be covered by a valid
    addrspace and word, if the addrspace contains words.

    Example:
    >>> import ucdp as u
    >>> from ucdp_addr import Addrspace, Word, Field, AddrMap
    >>> addrmap = AddrMap()
    >>> for aname in ("uart", "spi", "owi"):
    ...     addrspace = Addrspace(name=aname, width=32, depth=128)
    ...     addrmap.add(addrspace)
    ...     word = addrspace.add_word("ctrl")
    ...     field = word.add_field("ena", u.BitType(), "RW")
    ...     word = addrspace.add_word("stat")
    ...     field = word.add_field("bsy", u.BitType(), "RO")

    By string:

    >>> resolve(addrmap, "uart")
    AddrMapRef(..., addrspace=Addrspace(name='uart', ...))
    >>> resolve(addrmap, "uart.ctrl")
    AddrMapRef(..., addrspace=Addrspace(name='uart', ...), word=Word(name='ctrl', ...))
    >>> resolve(addrmap, "uart.ctrl.ena")
    AddrMapRef(..., addrspace=Addrspace(name='uart', ...), word=Word(name='ctrl', ...), field=Field(name='ena', ...))

    By reference:

    >>> ref = resolve(addrmap, "uart.ctrl.ena")
    >>> ref
    AddrMapRef(..., addrspace=Addrspace(name='uart', ...), word=Word(name='ctrl', ...), field=Field(name='ena', ...))
    >>> resolve(addrmap, ref)
    AddrMapRef(..., addrspace=Addrspace(name='uart', ...), word=Word(name='ctrl', ...), field=Field(name='ena', ...))

    By address space:

    >>> resolve(addrmap, Addrspace(baseaddr=0, width=32, depth=1))
    AddrMapRef(..., addrspace=Addrspace(name='uart', size=Bytesize('4 bytes')))

    By address range:

    >>> resolve(addrmap, AddrRange(baseaddr=0, width=32, depth=1))
    AddrMapRef(addrrange=AddrRange(size=Bytesize('4 bytes')))

    By address:

    >>> resolve(addrmap, 8)
    AddrMapRef(addrrange=AddrRange(baseaddr=Hex('0x8'), size=Bytesize('4 bytes')))

    Errors:

    >>> resolve(addrmap, "uart.missing")
    Traceback (most recent call last):
      ...
    ValueError: 'uart.missing' does not exists
    >>> resolve(addrmap, "uart:ctrl")
    Traceback (most recent call last):
      ...
    ValueError: uart:ctrl does not match pattern 'addrspace[.word[.field]]'
    >>> resolve(addrmap, 5.0)
    Traceback (most recent call last):
    ...
    TypeError: 5.0
    >>> resolve(addrmap, Addrspace(baseaddr=0x1000, width=32, depth=1))
    Traceback (most recent call last):
      ...
    ValueError: Addrspace(baseaddr=Hex('0x1000'), size=Bytesize('4 bytes')) does not exists
    """
    try:
        return next(iter(resolves(addrmap, item)))
    except StopIteration:
        raise ValueError(f"{item!r} does not exists") from None


def resolves(addrmap: AddrMap, item: ToAddrMapRef) -> Iterator[AddrMapRef]:
    """
    Same as `resolve` but returns all matches.

    >>> import ucdp as u
    >>> from ucdp_addr import Addrspace, Word, Field, AddrMap
    >>> addrmap = AddrMap()
    >>> for aname in ("uart", "spi", "owi"):
    ...     addrspace = Addrspace(name=aname, width=32, depth=128)
    ...     addrmap.add(addrspace)
    ...     word = addrspace.add_word("ctrl")
    ...     field = word.add_field("ena", u.BitType(), "RW")
    ...     word = addrspace.add_word("stat")
    ...     field = word.add_field("bsy", u.BitType(), "RO")

    >>> for item in resolves(addrmap, "*.ctrl.ena"): print(item)
    uart.ctrl.ena
    spi.ctrl.ena
    owi.ctrl.ena
    """
    if isinstance(item, str):
        # 'addrspace[.word[.field]]' reference
        yield from _resolve_pat(addrmap, item)

    elif isinstance(item, AddrMapRef):
        yield item

    elif isinstance(item, Addrspace):
        yield addrmap.get(item)

    elif isinstance(item, AddrRange):
        yield AddrMapRef(addrrange=item)

    elif isinstance(item, int):
        yield AddrMapRef(addrrange=AddrRange(baseaddr=item, size=4))

    else:
        raise TypeError(item)


def _resolve_pat(addrmap: AddrMap, pat: str) -> Iterator[AddrMapRef]:
    mat = _RE_RESOLVE.match(pat)
    if mat:
        apat, wpat, fpat = mat.group("apat", "wpat", "fpat")
        addrspaces = [addrspace for addrspace in addrmap.iter() if match(addrspace.name, apat)]
        if wpat:
            addrspace_words: list[tuple[Addrspace, Word]] = []
            for addrspace in addrspaces:
                addrspace_words.extend((addrspace, word) for word in addrspace.words if match(word.name, wpat))

            if fpat:
                # 'addrspace.word.field'
                for addrspace, word in addrspace_words:
                    for field in word.fields:
                        if match(field.name, fpat):
                            yield AddrMapRef.create(addrspace=addrspace, word=word, field=field)
            else:
                # 'addrspace.word'
                for addrspace, word in addrspace_words:
                    yield AddrMapRef.create(addrspace=addrspace, word=word)
        else:
            # 'addrspace'
            for addrspace in addrspaces:
                yield AddrMapRef.create(addrspace=addrspace)
    else:
        raise ValueError(f"{pat} does not match pattern 'addrspace[.word[.field]]'")
