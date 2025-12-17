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
Address Space.
"""

from collections import defaultdict
from collections.abc import Callable, Iterator
from itertools import chain
from string import ascii_lowercase
from typing import Any, Literal, Optional, TypeAlias

import pydantic as pyd
import ucdp as u
from humannum import bytesize_, int_
from icdutil import num
from ucdp_glbl.attrs import CastableAttrs, cast_attrs

from .access import Access, ToAccess, cast_access
from .addrrange import AddrRange

NamingScheme: TypeAlias = Literal["dec", "dec1", "alpha"] | Callable[[int], str]

_ALPHA_PER_DIGIT = len(ascii_lowercase)


class FullError(ValueError):
    """Full."""


class Field(u.IdentLightObject):
    """Field."""

    type_: u.BaseScalarType
    """Type."""
    bus: Access | None = None
    """Bus Access."""
    core: Access | None = None
    """Core Access."""
    offset: int | u.Expr
    """Rightmost Bit Position."""
    is_volatile: bool = False
    """Volatile."""
    doc: u.Doc = u.Doc()
    """Documentation."""
    attrs: CastableAttrs = ()
    """Attributes."""

    @property
    def title(self) -> str | None:
        """Alias to `doc.title`."""
        return self.doc.title

    @property
    def descr(self) -> str | None:
        """Alias to `doc.descr`."""
        return self.doc.descr

    @property
    def comment(self) -> str | None:
        """Alias to `doc.comment`."""
        return self.doc.comment

    @property
    def comment_or_title(self) -> str | None:
        """Return `comment` if set, otherwise `title`."""
        return self.doc.comment_or_title

    @property
    def slice(self) -> u.Slice:
        """Slice with Word."""
        return u.Slice(width=self.type_.width, right=self.offset)

    @property
    def is_const(self) -> bool:
        """Field is Constant."""
        return get_is_const(self.bus, self.core)

    @property
    def access(self) -> str:
        """Access."""
        bus = (self.bus and self.bus.name) or "-"
        core = (self.core and self.core.name) or "-"
        return f"{bus}/{core}"


FieldFilter = Callable[[Field], bool]


class Word(u.IdentObject):
    """Word."""

    fields: u.Namespace = u.Field(default_factory=u.Namespace, init=False, repr=False)
    """Fields within Word."""
    offset: int | u.Expr
    """Rightmost Word Position."""
    width: int
    """Width in Bits."""
    depth: int | u.Expr | None = None
    """Number of words."""
    doc: u.Doc = u.Doc()
    """Documentation"""
    attrs: CastableAttrs = ()
    """Attributes."""

    bus: Access | None = None
    core: Access | None = None
    is_volatile: bool | None = None

    @property
    def title(self) -> str | None:
        """Alias to `doc.title`."""
        return self.doc.title

    @property
    def descr(self) -> str | None:
        """Alias to `doc.descr`."""
        return self.doc.descr

    @property
    def comment(self) -> str | None:
        """Alias to `doc.comment`."""
        return self.doc.comment

    @property
    def comment_or_title(self) -> str | None:
        """Return `comment` if set, otherwise `title`."""
        return self.doc.comment_or_title

    def add_field(
        self,
        name: str,
        type_: u.BaseScalarType,
        bus: Access | str | None = None,
        core: Access | str | None = None,
        offset: int | u.Expr | None = None,
        align: int | u.Expr | None = None,
        is_volatile: bool | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        attrs: CastableAttrs | None = None,
        **kwargs,
    ) -> Field:
        """Add field."""
        if bus is not None:
            bus = cast_access(bus)
        else:
            bus = self.bus
        if core is not None:
            core = cast_access(core)
        else:
            core = self.core
        if self.fields:
            free = tuple(self.fields)[-1].slice.left + 1
        else:
            free = 0
        offset = num.align(free, offset=offset, align=align)
        doc = u.doc_from_type(type_, title=title, descr=descr, comment=comment)
        if is_volatile is None:
            is_volatile = self.is_volatile
        if is_volatile is None:
            is_volatile = get_is_volatile(bus, core)
        field = self._create_field(
            name=name,
            type_=type_,
            bus=bus,
            core=core,
            offset=offset,
            is_volatile=is_volatile,
            doc=doc,
            attrs=cast_attrs(attrs),
            **kwargs,
        )
        if field.slice.left >= self.width:
            raise FullError(f"Field {field.name!r} exceeds word width of {self.width}")
        self.fields.add(field)
        return field

    def _create_field(self, **kwargs) -> Field:
        return Field(**kwargs)

    @property
    def slice(self) -> u.Slice:
        """Slice with Address Space."""
        if self.depth is None:
            return u.Slice(left=self.offset, right=self.offset)
        return u.Slice(width=self.depth, right=self.offset)

    def lock(self):
        """Lock For Modification."""
        self.fields.lock()

    @property
    def wordsize(self) -> float:
        """Word Size in Bytes."""
        return self.width * (self.depth or 1) / 8

    @property
    def byteoffset(self) -> u.Hex:
        """Offset in Bytes, if word width is multiple of 8."""
        if (self.width % 8) != 0:
            raise ValueError(f"'byteoffset' is only available on words with 'width' multiple of 8 (not {self.width})")
        return self.offset * self.width // 8

    @property
    def access(self) -> str:
        """Access."""
        if self.bus or self.core:
            bus = (self.bus and self.bus.name) or "-"
            core = (self.core and self.core.name) or "-"
            return f"{bus}/{core}"
        return ""

    def get_field(self, name: str) -> Field:
        """Get Field."""
        return self.fields[name]

    def get_default(self, filter_=None) -> u.Hex:
        """
        Return Word default value for all fields of one word.

        >>> import ucdp_addr as ua
        >>> word = ua.Word(name='word', offset=0, width=32)
        >>> field = word.add_field('field0', u.UintType(3, default=3), ua.access.RO)
        >>> field = word.add_field('field1', u.SintType(6, default=-8), ua.access.WO, align=4)
        >>> field = word.add_field('field2', u.UintType(3, default=4), ua.access.RW, align=4)

        >>> word.get_default()
        Hex('0x00004383')
        >>> word.get_default(filter_=lambda field: field.bus.read)
        Hex('0x00004003')
        >>> word.get_default(filter_=lambda field: field.bus.write)
        Hex('0x00004380')
        >>> word.get_default(filter_=lambda field: field.bus.read and field.bus.write)
        Hex('0x00004000')
        """
        fields = self.fields
        if filter_:
            fields = [field for field in fields if filter_(field)]
        default = sum(
            [field.slice.update(0, field.type_.default, is_signed=u.is_signed(field.type_)) for field in fields]
        )
        return u.Hex(default, width=self.width)

    def get_mask(self, filter_=None) -> u.Hex:
        """
        Return mask for all fields of one word.

        >>> import ucdp_addr as ua
        >>> word = ua.Word(name='word', offset=0, width=32)
        >>> field = word.add_field('field0', u.UintType(3), ua.access.RO)
        >>> field = word.add_field('field1', u.UintType(6), ua.access.WO, align=4)
        >>> field = word.add_field('field2', u.UintType(3), ua.access.RW, align=4)

        >>> word.get_mask()
        Hex('0x000073F7')
        >>> word.get_mask(filter_=lambda field: field.bus.read)
        Hex('0x00007007')
        >>> word.get_mask(filter_=lambda field: field.bus.write)
        Hex('0x000073F0')
        >>> word.get_mask(filter_=lambda field: field.bus.read and field.bus.write)
        Hex('0x00007000')
        """
        return get_mask(self, filter_=filter_)


def _bytealign(width, free, offset=None, align=None, byteoffset=None, bytealign=None):
    if byteoffset is None and bytealign is None:
        pass
    elif (width % 8) == 0:
        bytesperword = width // 8
        if byteoffset is not None:
            if offset is not None:
                raise ValueError("'byteoffset' and 'offset' are mutually exclusive")
            offset = byteoffset // bytesperword
        if bytealign is not None:
            if align is not None:
                raise ValueError("'bytealign' and 'align' are mutually exclusive")
            align = bytealign // bytesperword
    else:
        raise ValueError(f"'byteoffset/bytealign' are only available on 'width' multiple of 8 (not {width})")
    return num.align(free, offset=offset, align=align)


WordFilter = Callable[[Word], bool]
WordFields = tuple[Word, tuple[Field, ...]]

FillWordFactory = Callable[["Addrspace", int, int, int], Word]
FillFieldFactory = Callable[[Word, int, int, int], Field]


class Words(u.Object):
    """Multiple Related Words."""

    model_config = pyd.ConfigDict(
        frozen=False,
    )

    name: str
    addrspace: "Addrspace"
    word_kwargs: dict[str, Any]
    naming: NamingScheme = "dec"

    idx: int
    """Next Word Index."""
    word: Word
    """Current Word."""
    words: list[Word]

    @classmethod
    def create(
        cls, name: str, addrspace: "Addrspace", word_kwargs: dict[str, Any], naming: NamingScheme = "dec", **kwargs
    ) -> "Words":
        """Create Helper for Set of Words."""
        idx, word = cls._create_word(name, addrspace, word_kwargs, naming, **kwargs)
        return cls(
            name=name, addrspace=addrspace, word_kwargs=word_kwargs, idx=idx, word=word, words=[word], naming=naming
        )

    @staticmethod
    def _create_word(
        name: str, addrspace: "Addrspace", word_kwargs: dict[str, Any], naming: NamingScheme, idx: int = 0, **kwargs
    ) -> tuple[int, Word]:
        if naming == "dec":
            suffix = str(idx)
        elif naming == "dec1":
            suffix = str(idx + 1)
        elif naming == "alpha":
            suffix = name_alpha(idx)
        else:
            suffix = naming(idx)
        word = addrspace.add_word(f"{name}{suffix}", **word_kwargs, **kwargs)
        return idx + 1, word

    def _add_field(self, *args, **kwargs) -> Field:
        return self.word.add_field(*args, **kwargs)

    def next(self):
        """Start a new Word."""
        self.idx, self.word = self._create_word(self.name, self.addrspace, self.word_kwargs, self.naming, idx=self.idx)
        self.words.append(self.word)

    def add_field(self, *args, **kwargs) -> Field:
        """Add Field to Current Word or start a new one."""
        try:
            return self._add_field(*args, **kwargs)
        except FullError:
            self.next()
            return self._add_field(*args, **kwargs)

    @property
    def fields(self) -> tuple[Field, ...]:
        """Fields Of All Words."""
        return tuple(chain.from_iterable(word.fields for word in self.words))


class Addrspace(AddrRange, u.IdentObject):
    """Address Space."""

    name: str = ""
    """Name."""
    is_sub: bool = True
    """Address Decoder Just Compares `addrwidth` LSBs."""
    words: u.Namespace = u.Field(default_factory=u.Namespace, repr=False)
    """Words within Address Space."""
    doc: u.Doc = u.Doc()
    """Documentation"""
    attrs: CastableAttrs = ()
    """Attributes."""

    add_words_naming: NamingScheme = "dec"
    """Naming Scheme for words created by `add_words`."""

    bus: ToAccess | None = None
    core: ToAccess | None = None
    is_volatile: bool | None = None

    @property
    def title(self) -> str | None:
        """Alias to `doc.title`."""
        return self.doc.title

    @property
    def descr(self) -> str | None:
        """Alias to `doc.descr`."""
        return self.doc.descr

    @property
    def comment(self) -> str | None:
        """Alias to `doc.comment`."""
        return self.doc.comment

    @property
    def comment_or_title(self) -> str | None:
        """Return `comment` if set, otherwise `title`."""
        return self.doc.comment_or_title

    @property
    def size_used(self) -> u.Bytes:
        """Number of Bytes Used."""
        return bytesize_(int(sum(word.wordsize for word in self.words)))

    @property
    def free_offset(self) -> int:
        """Free Offset."""
        if self.words:
            return tuple(self.words)[-1].slice.left + 1
        return 0

    @property
    def info(self) -> str:
        """Info."""
        return str(self)

    def __str__(self) -> str:
        baseaddr = f"+{self.baseaddr}" if self.is_sub else f"{self.baseaddr}"
        return f"{self.name} {baseaddr} {self.depth}x{self.width}"

    @property
    def base(self) -> str:
        """Base."""
        if self.is_sub:
            return f"+{self.baseaddr}"
        return f"{self.baseaddr}"

    @property
    def access(self) -> str:
        """Access."""
        if self.bus or self.core:
            bus = (self.bus and self.bus.name) or "-"
            core = (self.core and self.core.name) or "-"
            return f"{bus}/{core}"
        return ""

    def add_word(
        self,
        name: str,
        offset: int | u.Expr | None = None,
        align: int | u.Expr | None = None,
        byteoffset: int | u.Expr | None = None,
        bytealign: int | u.Expr | None = None,
        depth: int | u.Expr | None = None,
        bus: Access | str | None = None,
        core: Access | str | None = None,
        is_volatile: bool | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        **kwargs,
    ) -> Word:
        """Add Word."""
        free = self.free_offset
        offset = _bytealign(self.width, free, offset=offset, align=align, byteoffset=byteoffset, bytealign=bytealign)
        doc = u.Doc(title=title, descr=descr, comment=comment)
        if bus is None:
            bus = self.bus
        else:
            bus = cast_access(bus)
        if core is None:
            core = self.core
        else:
            core = cast_access(core)
        if is_volatile is None:
            is_volatile = self.is_volatile
        word = self._create_word(
            name=name,
            offset=offset,
            width=self.width,
            depth=depth,
            doc=doc,
            bus=bus,
            core=core,
            is_volatile=is_volatile,
            **kwargs,
        )
        if word.slice.left >= self.depth:
            raise FullError(f"Word {word.name!r} exceeds address space depth of {self.depth}")
        if word.depth == 0:
            raise ValueError(f"Word {word.name!r} has illegal depth of zero.")
        self.words.add(word)
        return word

    def add_words(
        self,
        name: str,
        offset: int | u.Expr | None = None,
        align: int | u.Expr | None = None,
        byteoffset: int | u.Expr | None = None,
        bytealign: int | u.Expr | None = None,
        depth: int | u.Expr | None = None,
        naming: NamingScheme | None = None,
        **kwargs,
    ) -> Words:
        """Add Word."""
        if depth is not None:
            raise ValueError("'depth' is not supported on add_words()")
        return self._create_words(
            name=name,
            addrspace=self,
            word_kwargs=kwargs,
            offset=offset,
            align=align,
            byteoffset=byteoffset,
            bytealign=bytealign,
            naming=naming or self.add_words_naming,
        )

    def get_word(self, name: str) -> Word:
        """Retrieve Word."""
        return self.words[name]

    def _create_word(self, **kwargs) -> Word:
        return Word(**kwargs)

    def _create_words(self, **kwargs) -> Words:
        return Words.create(**kwargs)

    def lock(self):
        """Lock For Modification."""
        for word in self.words:
            word.lock()
        self.words.lock()

    def get_word_hiername(self, word: Word) -> str:
        """Get Hierarchical Word Name."""
        return f"{self.name}.{word.name}"

    def get_field_hiername(self, word: Word, field: Field) -> str:
        """Get Hierarchical Field Name."""
        return f"{self.name}.{word.name}.{field.name}"

    def iter(  # noqa: C901
        self,
        wordfilter: WordFilter | None = None,
        fieldfilter: FieldFilter | None = None,
        fill: bool | None = None,
        fill_word: FillWordFactory | bool | None = None,
        fill_field: FillFieldFactory | bool | None = None,
        fill_word_end: bool | None = None,
        fill_field_end: bool | None = None,
    ) -> Iterator[WordFields]:
        """Iterate over words and their fields."""
        if fill is not None:
            fill_word = fill if fill_word is None else fill_word
            fill_field = fill if fill_field is None else fill_field
            fill_word_end = fill if fill_word_end is None else fill_word_end
            fill_field_end = fill if fill_field_end is None else fill_field_end

        def no_wordfilter(_: Word) -> bool:
            return True

        wordfilter = wordfilter or no_wordfilter

        def no_fieldfilter(_: Word) -> bool:
            return True

        fieldfilter = fieldfilter or no_fieldfilter

        if fill_word is True:
            fill_word = create_fill_word

        if fill_field is True:
            fill_field = create_fill_field

        def create_word(counter, offset, size) -> WordFields:
            idx = counter[None]
            fword = fill_word(self, idx, offset, size)  # type: ignore[operator]
            counter[None] = idx + 1
            if fill_field and fill_field_end:
                return fword, (fill_field(fword, 0, 0, word.width),)
            return fword, ()

        def fill_fields(word, fields) -> Iterator:
            offset = 0
            idx = 0
            for field in fields:
                if not fieldfilter(field):
                    continue

                # fill before
                if field.offset > offset:
                    yield fill_field(word, idx, offset, field.offset - offset)
                    idx += 1

                yield field

                offset = field.slice.nxt

            if fill_field_end:
                if word.width > offset:
                    yield fill_field(word, idx, offset, word.width - offset)

        counter: dict[None, int] = defaultdict(int)
        offset = 0
        for word in self.words:
            if not wordfilter(word):
                continue

            # fill before
            if fill_word and word.offset > offset:
                yield create_word(counter, offset, word.offset - offset)
                offset = word.offset + (word.depth or 1)

            if fill_field:
                fields = tuple(fill_fields(word, word.fields))
            else:
                fields = tuple(field for field in word.fields if fieldfilter(field))

            if fields:
                yield word, fields
                offset = word.offset + (word.depth or 1)

        if fill_word and fill_word_end:
            yield create_word(counter, offset, self.depth - offset)

    def is_overlapping(self, other: "Addrspace") -> bool:
        """
        Determine both Address Spaces Overlap.

            >>> one = Addrspace(name='one', baseaddr=0x2000, size='4kB')
            >>> two = Addrspace(name='two', baseaddr=0x3000, size='4kB')
            >>> three = Addrspace(name='three', baseaddr=0x2000, size='5kB')
            >>> one.is_overlapping(two)
            False
            >>> one.is_overlapping(three)
            True
            >>> three.is_overlapping(one)
            True
            >>> three.is_overlapping(two)
            True
        """
        if self.baseaddr < other.baseaddr:
            return self.endaddr >= other.baseaddr
        return self.baseaddr <= other.endaddr

    def get_intersect(self, other: "Addrspace") -> Optional["Addrspace"]:
        """
        Get Intersection.

            >>> one = Addrspace(name='one', baseaddr=0x2000, size='4kB')
            >>> two = Addrspace(name='two', baseaddr=0x3000, size='4kB')
            >>> three = Addrspace(name='three', baseaddr=0x2000, size='5kB')
            >>> one.get_intersect(two)
            >>> one.get_intersect(three)
            Addrspace(name='one', baseaddr=Hex('0x2000'), size=Bytesize('4 KB'))
            >>> three.get_intersect(one)
            Addrspace(name='three', baseaddr=Hex('0x2000'), size=Bytesize('4 KB'))
            >>> three.get_intersect(two)
            Addrspace(name='three', baseaddr=Hex('0x3000'), size=Bytesize('1 KB'))
        """
        baseaddr = max(self.baseaddr, other.baseaddr)
        endaddr = min(self.endaddr, other.endaddr)
        size = endaddr - baseaddr + 1
        if size <= 0:
            return None
        words = u.Namespace()
        # TODO: add words
        return self.new(baseaddr=baseaddr, size=size, depth=None, words=words)

    def join(self, other: "Addrspace") -> Optional["Addrspace"]:
        """
        Join if Possible.

        TODO: doc
        """
        if other.is_sub:
            return self._join(self, other)
        if self.is_sub:
            return self._join(other, self)
        return other.get_intersect(self)

    @staticmethod
    def _join(one: "Addrspace", sub: "Addrspace") -> Optional["Addrspace"]:
        baseaddr = one.baseaddr + sub.baseaddr
        endaddr = one.baseaddr + sub.endaddr
        if endaddr > one.endaddr:
            raise ValueError(f"{sub!r} does not fit into {one!r}")
        return sub.new(baseaddr=baseaddr, size=min(one.size, sub.size), is_sub=one.is_sub, words=sub.words)


def get_is_volatile(bus: Access | None, core: Access | None) -> bool:
    """Calc Volatile Flag based on Accesses."""
    if bus is not None:
        if bus.read and bus.read.data is not None:
            # Read operation on bus manipulates data
            return True
        if core is None:
            # Bus Access Only
            return False
    if core is not None:
        if core.read and core.read.data is not None:
            # Read operation on core side manipulates data
            return True
        if bus is not None and bus.write and core.write:
            # Two-Sides can manipulate
            return True
    return False


def get_is_const(bus: Access | None, core: Access | None) -> bool:
    """Calc Is Constant Flag based on Accesses."""
    if bus is not None:
        if bus.write is not None:
            return False
        if bus.read and bus.read.data is not None:
            return False
    if core is not None:
        if core.read and core.read.data is not None:
            return False
        if core.write is not None:
            return False
    return True


__dec_to_alpha = ("", *ascii_lowercase)


def name_alpha(num: int) -> str:
    """
    Convert number to a alpha digit.

    >>> name_alpha(0)
    'a'
    >>> name_alpha(25)
    'z'
    >>> name_alpha(26)
    'aa'
    >>> name_alpha(27)
    'ab'
    >>> name_alpha(26+25)
    'az'
    >>> name_alpha(26+26)
    'ba'
    >>> name_alpha(26+26+25)
    'bz'
    >>> name_alpha(1000)
    'alm'
    """
    num += 1

    if num < _ALPHA_PER_DIGIT:
        return __dec_to_alpha[num]

    result: list[str] = []
    while num:
        num, rem = divmod(num, _ALPHA_PER_DIGIT)
        result.insert(0, __dec_to_alpha[rem])
        if not rem:
            num -= 1
            result.insert(0, "z")
    return "".join(result)


def create_fill_word(addrspace, idx, offset, depth) -> Word:
    """Create Fill Word."""
    return Word(name=f"reserved{idx}", offset=offset, depth=depth, width=addrspace.width)


def create_fill_field(word, idx, offset, width) -> Field:
    """Create Fill Field."""
    return Field(name=f"reserved{idx}", type_=u.UintType(width), offset=offset)


class ReservedAddrspace(Addrspace):
    """A Reserved Address Space."""


class DefaultAddrspace(Addrspace):
    """Default Address Space."""

    name: str = u.Field(init=False, default="")


def resolve_field_value(field: Field, value: int | str) -> int:
    """Resolve Enumeration If necessary."""
    type_ = field.type_
    if value == "<RST>":
        return field.type_.default
    if not isinstance(type_, u.BaseEnumType) or not isinstance(value, str):
        return int_(value)[0]
    for item in type_.values():
        if item.value == value:
            return item.key
    # value is a string but not an enum value, so we need to check if
    # it is castable to int, might be an int, bit or hex string
    if isinstance(value, str):
        try:
            val, _ = int_(value)
            return val
        except ValueError:
            # drop down to our general, prettier error message below
            pass
    raise ValueError(f"Value {value!r} is not covered by {type_}")


def get_mask(word: Word, filter_=None) -> u.Hex:
    """
    Return mask for all fields of one word.

    >>> import ucdp_addr as ua
    >>> word = ua.Word(name='word', offset=0, width=32)
    >>> field = word.add_field('field0', u.UintType(3), ua.access.RO)
    >>> field = word.add_field('field1', u.UintType(6), ua.access.WO, align=4)
    >>> field = word.add_field('field2', u.UintType(3), ua.access.RW, align=4)

    >>> get_mask(word)
    Hex('0x000073F7')
    >>> get_mask(word, filter_=lambda field: field.bus.read)
    Hex('0x00007007')
    >>> get_mask(word, filter_=lambda field: field.bus.write)
    Hex('0x000073F0')
    >>> get_mask(word, filter_=lambda field: field.bus.read and field.bus.write)
    Hex('0x00007000')
    """
    fields = word.fields
    if filter_:
        fields = [field for field in fields if filter_(field)]
    mask = sum([field.slice.mask for field in fields])
    return u.Hex(mask, width=word.width)


def read_on_modify(word: Word, mask: int) -> bool:
    """
    Return `True` if a read is needed in read-modify-write operations on word `word` with `mask`.

    >>> import ucdp_addr as ua
    >>> word = ua.Word(name='word', offset=0, width=32)
    >>> field = word.add_field('field0', u.UintType(3), ua.access.RO)
    >>> field = word.add_field('field1', u.UintType(6), ua.access.WO, align=4)
    >>> field = word.add_field('field2', u.UintType(3), ua.access.RW, align=4)

    >>> read_on_modify(word, 0x00007000)
    False
    >>> read_on_modify(word, 0x00003000)
    True
    """
    rwmask = get_mask(word, lambda field: field.bus.read and field.bus.write)
    return bool(rwmask) and rwmask != mask
