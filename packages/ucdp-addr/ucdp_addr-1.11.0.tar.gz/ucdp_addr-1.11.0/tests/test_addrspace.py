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
#
"""Test Address Space."""

import re

import ucdp as u
from pytest import fixture, mark, raises
from test2ref import assert_refdata
from ucdp_glbl.attrs import Attr

from ucdp_addr import DefaultAddrspace, zip_addrspaces
from ucdp_addr.access import ACCESSES, RO, RW
from ucdp_addr.addrspace import (
    Addrspace,
    Field,
    Word,
    Words,
    create_fill_field,
    create_fill_word,
    get_is_const,
    get_is_volatile,
)


@fixture
def word():
    """Example Word."""
    yield Word(name="word", offset=0, width=32)


@fixture
def addrspace():
    """Example Address Space."""
    yield Addrspace(name="name", depth=32)


def test_accesses(tmp_path, capsys):
    """Test Accesses."""
    for access in ACCESSES:
        print(f"{access!s}")
        print(f"    {access.read=!r}")
        print(f"    {access.write=!r}")
        print(f"    {access.title=!r}")
        print(f"    {access.descr=!r}")
    assert_refdata(test_accesses, tmp_path, capsys=capsys)


def test_add_field(addrspace, word):  # noqa: PLR0915
    """Add Field."""
    field0 = word.add_field("field0", u.UintType(20), "RW", comment="my comment")
    assert field0.name == "field0"
    assert field0.type_ == u.UintType(20)
    assert field0.bus == RW
    assert field0.core is None
    assert field0.offset == 0
    assert field0.slice == u.Slice("19:0")
    assert field0.access == "RW/-"
    assert field0.doc == u.Doc(comment="my comment")
    assert field0.title is None
    assert field0.descr is None
    assert field0.comment == "my comment"
    assert field0.comment_or_title == "my comment"

    field1 = word.add_field("field1", u.SintType(6), "RO", core="RO", title="my title", descr="my descr")
    assert field1.name == "field1"
    assert field1.type_ == u.SintType(6)
    assert field1.bus == RO
    assert field1.core == RO
    assert field1.offset == 20
    assert field1.slice == u.Slice("25:20")
    assert field1.access == "RO/RO"
    assert field1.doc == u.Doc(title="my title", descr="my descr")
    assert field1.title == "my title"
    assert field1.descr == "my descr"
    assert field1.comment is None
    assert field1.comment_or_title == "my title"

    assert tuple(word.fields) == (field0, field1)

    field2 = word.add_field("field2", u.UintType(2), "RO", align=4)
    assert field2.name == "field2"
    assert field2.type_ == u.UintType(2)
    assert field2.bus == RO
    assert field2.core is None
    assert field2.offset == 28
    assert field2.slice == u.Slice("29:28")
    assert field2.access == "RO/-"
    assert field2.doc == u.Doc()
    assert field2.title is None
    assert field2.descr is None
    assert field2.comment is None
    assert field2.comment_or_title is None

    with raises(ValueError, match=re.escape("Field 'field3' exceeds word width of 32")):
        word.add_field("field3", u.UintType(3), "RO", offset=30)

    field4 = word.add_field("field4", u.UintType(2), "RO", offset=30)
    assert field4.slice == u.Slice("31:30")

    assert tuple(word.fields) == (field0, field1, field2, field4)

    assert word.get_field("field2") is field2

    assert addrspace.get_field_hiername(word, field0) == "name.word.field0"
    assert addrspace.get_field_hiername(word, field1) == "name.word.field1"

    assert word.get_mask() == u.Hex("0xF3FFFFFF")
    assert word.get_mask(filter_=lambda field: field.bus) == u.Hex("0xF3FFFFFF")
    assert word.get_mask(filter_=lambda field: field.core) == u.Hex("0x03F00000")


def test_add_word(addrspace):  # noqa: PLR0915
    """Add Word."""
    word0 = addrspace.add_word("word0", comment="my comment")
    assert word0.name == "word0"
    assert word0.offset == 0
    assert word0.width == 32
    assert word0.depth is None
    assert word0.slice == u.Slice("0")
    assert word0.bus is None
    assert word0.core is None
    assert word0.doc == u.Doc(comment="my comment")
    assert word0.title is None
    assert word0.descr is None
    assert word0.comment == "my comment"
    assert word0.comment_or_title == "my comment"

    word1 = addrspace.add_word("word1", offset=6, title="my title", descr="my descr")
    assert word1.name == "word1"
    assert word1.offset == 6
    assert word1.width == 32
    assert word1.depth is None
    assert word1.slice == u.Slice("6")
    assert word1.doc == u.Doc(title="my title", descr="my descr")
    assert word1.title == "my title"
    assert word1.descr == "my descr"
    assert word1.comment is None
    assert word1.comment_or_title == "my title"

    word2 = addrspace.add_word("word2", align=4, depth=2)
    assert word2.name == "word2"
    assert word2.offset == 8
    assert word2.width == 32
    assert word2.depth == 2
    assert word2.slice == u.Slice("9:8")
    assert word2.doc == u.Doc()
    assert word2.title is None
    assert word2.descr is None
    assert word2.comment is None
    assert word2.comment_or_title is None

    with raises(ValueError, match=re.escape("Word 'word3' exceeds address space depth of 32")):
        addrspace.add_word("word3", offset=32)

    word4 = addrspace.add_word("word4", offset=31, bus="RW", core="RO")
    assert word4.name == "word4"
    assert word4.offset == 31
    assert word4.width == 32
    assert word4.depth is None
    assert word4.slice == u.Slice("31")
    assert word4.bus == RW
    assert word4.core == RO

    with raises(ValueError, match=re.escape("Word 'word5' has illegal depth of zero.")):
        addrspace.add_word("word5", depth=0)

    assert tuple(addrspace.words) == (word0, word1, word2, word4)

    assert addrspace.get_word_hiername(word0) == "name.word0"
    assert addrspace.get_word_hiername(word1) == "name.word1"

    assert tuple(addrspace.iter()) == ()

    assert addrspace.get_word("word2") is word2


def test_addrspace():
    """Address Space."""
    addrspace = Addrspace(name="name", depth=1024)
    assert addrspace.name == "name"
    assert addrspace.words == u.Namespace()
    assert addrspace.width == 32
    assert addrspace.depth == 1024
    assert addrspace.size == u.Bytesize("4 KB")
    assert addrspace.addrwidth == 12
    assert addrspace.baseaddr == u.Hex("0x0")
    assert addrspace.endaddr == u.Hex("0xFFF")
    assert addrspace.nextaddr == u.Hex("0x1000")
    assert addrspace.size_used == u.Bytesize("0 KB")
    assert addrspace.wordsize == 4
    assert addrspace.doc == u.Doc()
    assert addrspace.title is None
    assert addrspace.descr is None
    assert addrspace.comment is None
    assert addrspace.comment_or_title is None


def test_addrspace_custom():
    """Address Space."""
    addrspace = Addrspace(
        name="name", width=64, depth=128, baseaddr=0x10000, doc=u.Doc(title="my title", descr="my descr")
    )
    assert addrspace.name == "name"
    assert addrspace.words == u.Namespace()
    assert addrspace.width == 64
    assert addrspace.depth == 128
    assert addrspace.size == u.Bytesize("1 KB")
    assert addrspace.addrwidth == 10
    assert addrspace.baseaddr == u.Hex("0x10000")
    assert addrspace.endaddr == u.Hex("0x103FF")
    assert addrspace.nextaddr == u.Hex("0x10400")
    assert addrspace.size_used == u.Bytesize("0 KB")
    assert addrspace.doc == u.Doc(title="my title", descr="my descr")
    assert addrspace.title == "my title"
    assert addrspace.descr == "my descr"
    assert addrspace.comment is None
    assert addrspace.comment_or_title == "my title"


def test_addrspace_size():
    """Address Space with Size."""
    addrspace = Addrspace(name="name", width=64, size="4MB")
    assert addrspace.name == "name"
    assert addrspace.words == u.Namespace()
    assert addrspace.width == 64
    assert addrspace.depth == 4 * 1024 * 1024 // 8
    assert addrspace.size == u.Bytesize("4 MB")
    assert addrspace.addrwidth == 22
    assert addrspace.baseaddr == u.Hex("0x0")
    assert addrspace.endaddr == u.Hex("0x3FFFFF")
    assert addrspace.nextaddr == u.Hex("0x400000")
    assert addrspace.size_used == u.Bytesize("0 KB")
    assert addrspace.wordsize == 8


def test_addrspace_depth_size_both():
    """Address Space with Depth and Size."""
    msg = "'depth' and 'size' are mutually exclusive."
    with raises(ValueError, match=re.escape(msg)):
        Addrspace(depth=128, size=1024)


def test_addrspace_depth_size_missing():
    """Address Space with Depth and Size Missing."""
    msg = "Either 'depth' or 'size' are required."
    with raises(ValueError, match=re.escape(msg)):
        Addrspace()


def test_addrspace_size_used(addrspace):
    """Address Space Size Used."""
    assert addrspace.size_used == u.Bytesize("0 KB")
    addrspace.add_word("one")
    assert addrspace.size_used == u.Bytesize("4 Bytes")
    addrspace.add_word("two", depth=8, align=8)
    assert addrspace.size_used == u.Bytesize("36 Bytes")


def test_lock():
    """Lock Mechanism."""
    addrspace = Addrspace(name="name", depth=1024)
    words = []
    for widx in range(3):
        word = addrspace.add_word(f"word{widx}")
        words.append(word)
        for fidx in range(3):
            word.add_field(f"field{fidx}", u.BitType(), "RO")

    assert addrspace.words.is_locked is False
    assert any(word.fields.is_locked for word in words) is False

    addrspace.lock()

    assert addrspace.words.is_locked is True
    assert all(word.fields.is_locked for word in words) is True


def test_volatile(tmp_path):
    """Test Volatile."""
    overview_file = tmp_path / "overview.md"
    with overview_file.open("w", encoding="utf-8") as file:
        for bus in (None, *ACCESSES):
            for core in (None, *ACCESSES):
                is_volatile = " V" if get_is_volatile(bus, core) else "  "
                is_const = " Const" if get_is_const(bus, core) else " FF"
                busstr = (bus and bus.name) or "-"
                corestr = (core and core.name) or "-"
                file.write(f"{busstr:8s} {corestr:8s}{is_volatile}{is_const}\n")

    assert_refdata(test_volatile, tmp_path)


def test_iter(addrspace):
    """Iteration."""
    a = addrspace.add_word("a")
    a0 = a.add_field("a0", u.BitType(), "RW")

    addrspace.add_word("b")
    c = addrspace.add_word("c")
    c0 = c.add_field("c0", u.BitType(), "RW")
    c1 = c.add_field("c1", u.BitType(), "RW")

    assert tuple(addrspace.iter()) == ((a, (a0,)), (c, (c0, c1)))
    result = ((c, (c0, c1)),)
    assert tuple(addrspace.iter(fieldfilter=lambda field: field.name.startswith("c"))) == result
    result = ((a, (a0,)),)
    assert tuple(addrspace.iter(wordfilter=lambda word: word.name.startswith("a"))) == result


def test_join():
    """Join Operation."""
    f = Addrspace(name="f", baseaddr=0x0, size="4GB", is_sub=False)
    f_s = Addrspace(name="f_s", baseaddr=0x0, size="4GB", is_sub=True)
    m = Addrspace(name="m", baseaddr=0x0000, size="1MB", is_sub=False)
    n = Addrspace(name="n", baseaddr=0xF000_0000, size="1MB", is_sub=False)
    a = Addrspace(name="a", baseaddr=0x2000, size="4KB", is_sub=False)
    a_s = Addrspace(name="a_s", baseaddr=0x2000, size="4KB", is_sub=True)

    assert m.join(a) == a
    assert n.join(a) is None

    assert m.join(a_s) == Addrspace(name="a_s", baseaddr=0x2000, size="4KB", is_sub=False)
    assert n.join(a_s) == Addrspace(name="a_s", baseaddr=0xF000_2000, size="4KB", is_sub=False)

    msg = "does not fit into Addrspace(name='o', "
    with raises(ValueError, match=re.escape(msg)):
        Addrspace(name="o", baseaddr=0xF000_0000, size="2KB", is_sub=False).join(a_s)

    msg = "does not fit into Addrspace(name='a_s', "
    with raises(ValueError, match=re.escape(msg)):
        a_s.join(f_s)

    assert a_s.join(m) == Addrspace(name="a_s", baseaddr=0x2000, depth=1024, is_sub=False)
    assert a_s.join(n) == Addrspace(name="a_s", baseaddr=0xF0002000, depth=1024, is_sub=False)

    assert f.join(f_s) == Addrspace(name="f_s", size="4 GB", is_sub=False)
    assert f_s.join(f) == Addrspace(name="f_s", size="4 GB", is_sub=False)


def test_addrspace_nodefaults():
    """No Defaults."""
    addrspace = Addrspace(name="name", depth=64)
    assert addrspace.bus is None
    assert addrspace.core is None

    word = addrspace.add_word("word")
    assert word.bus is None
    assert word.core is None

    field = word.add_field("field", u.BitType())
    assert field.bus is None
    assert field.core is None


def test_addrspace_defaults():
    """Defaults."""
    addrspace = Addrspace(name="name", bus="RO", core="RW", depth=64)
    assert addrspace.bus == RO
    assert addrspace.core == RW

    word = addrspace.add_word("word")
    assert word.bus == RO
    assert word.core == RW

    field = word.add_field("field", u.BitType())
    assert field.bus == RO
    assert field.core == RW


def test_word_bytewise(addrspace):
    """Test Byte-Wise."""
    word = addrspace.add_word("one", byteoffset=8)
    assert word.offset == 2
    assert word.byteoffset == 8

    word = addrspace.add_word("two", bytealign=8)
    assert word.offset == 4
    assert word.byteoffset == 16

    msg = "'byteoffset' and 'offset' are mutually exclusive"
    with raises(ValueError, match=re.escape(msg)):
        addrspace.add_word("three", byteoffset=8, offset=5)

    msg = "'bytealign' and 'align' are mutually exclusive"
    with raises(ValueError, match=re.escape(msg)):
        addrspace.add_word("three", bytealign=8, align=5)


def test_word_nonbyte():
    """Non-Byte wise."""
    addrspace = Addrspace(name="name", width=12, depth=64)

    msg = "'byteoffset/bytealign' are only available on 'width' multiple of 8 (not 12)"
    with raises(ValueError, match=re.escape(msg)):
        addrspace.add_word("one", byteoffset=4)

    msg = "'byteoffset/bytealign' are only available on 'width' multiple of 8 (not 12)"
    with raises(ValueError, match=re.escape(msg)):
        addrspace.add_word("one", bytealign=4)

    msg = "'byteoffset' is only available on words with 'width' multiple of 8 (not 10)"
    with raises(ValueError, match=re.escape(msg)):
        assert Word(name="word", width=10, offset=2).byteoffset


def test_word_access():
    """Word Access."""
    assert Word(name="word", width=8, offset=2).access == ""

    assert Word(name="word", width=8, offset=2, bus=RO).access == "RO/-"

    assert Word(name="word", width=8, offset=2, core=RO).access == "-/RO"

    assert Word(name="word", width=8, offset=2, bus=RW, core=RO).access == "RW/RO"


def test_addrspace_access():
    """Addressspace Access."""
    assert Addrspace(name="word", width=8, depth=2).access == ""

    assert Addrspace(name="word", width=8, depth=2, bus=RO).access == "RO/-"

    assert Addrspace(name="word", width=8, depth=2, core=RO).access == "-/RO"

    assert Addrspace(name="word", width=8, depth=2, bus=RW, core=RO).access == "RW/RO"


@fixture
def sparse_addrspace():
    """Sparse Address Space."""
    addrspace = Addrspace(name="name", depth=32)

    addrspace.add_word("empty", offset=2)

    word = addrspace.add_word("word0", offset=10)
    word.add_field("field0", u.UintType(2))

    word = addrspace.add_word("word1")
    word.add_field("field1", u.UintType(32))

    word = addrspace.add_word("word2", offset=20)
    word.add_field("field0", u.UintType(2), offset=8)
    word.add_field("field1", u.UintType(4), offset=16)

    yield addrspace


def _dump_addrspace(iterable, tmp_path, name="dump"):
    with (tmp_path / f"{name}.txt").open("w") as file:
        for word, fields in iterable:
            file.write(f"{word}\n")
            for field in fields:
                file.write(f"  {field}\n")


def _create_word(addrspace, idx, offset, depth):
    return Word(name=f"fillword{idx}", offset=offset, depth=depth, width=addrspace.width)


def _create_field(word, idx, offset, width):
    return Field(name=f"fillfield{idx}", type_=u.UintType(width), offset=offset)


def test_addrspace_iter(sparse_addrspace, tmp_path):
    """Iterate."""
    _dump_addrspace(sparse_addrspace.iter(), tmp_path)
    assert_refdata(test_addrspace_iter, tmp_path)


def test_addrspace_iter_fill_word(sparse_addrspace, tmp_path):
    """Iterate with word filling."""
    _dump_addrspace(sparse_addrspace.iter(fill_word=_create_word), tmp_path, name="dump")
    _dump_addrspace(sparse_addrspace.iter(fill_word=True), tmp_path, name="dump-true")
    _dump_addrspace(
        sparse_addrspace.iter(fill_word=True, wordfilter=lambda word: word.name != "word0"),
        tmp_path,
        name="dump-true-filter",
    )
    _dump_addrspace(sparse_addrspace.iter(fill_word=_create_word, fill_word_end=True), tmp_path, name="dump_end")
    assert_refdata(test_addrspace_iter_fill_word, tmp_path)


def test_addrspace_iter_fill_field(sparse_addrspace, tmp_path):
    """Iterate with field filling."""
    _dump_addrspace(sparse_addrspace.iter(fill_field=_create_field), tmp_path, name="dump")
    _dump_addrspace(sparse_addrspace.iter(fill_field=True), tmp_path, name="dump-true")
    _dump_addrspace(
        sparse_addrspace.iter(fill_field=True, fieldfilter=lambda field: field.name != "field1"),
        tmp_path,
        name="dump-true-filter",
    )
    _dump_addrspace(sparse_addrspace.iter(fill_field=_create_field, fill_field_end=True), tmp_path, name="dump_end")
    assert_refdata(test_addrspace_iter_fill_field, tmp_path)


def test_addrspace_iter_fill_word_fill_field(sparse_addrspace, tmp_path):
    """Iterate with filling."""
    _dump_addrspace(sparse_addrspace.iter(fill_word=_create_word, fill_field=_create_field), tmp_path, name="dump_0_0")
    _dump_addrspace(
        sparse_addrspace.iter(fill_word=_create_word, fill_field=_create_field, fill_word_end=True),
        tmp_path,
        name="dump_1_0",
    )
    _dump_addrspace(
        sparse_addrspace.iter(fill_word=_create_word, fill_field=_create_field, fill_field_end=True),
        tmp_path,
        name="dump_0_1",
    )
    _dump_addrspace(
        sparse_addrspace.iter(
            fill_word=_create_word, fill_field=_create_field, fill_word_end=True, fill_field_end=True
        ),
        tmp_path,
        name="dump_1_1",
    )
    assert_refdata(test_addrspace_iter_fill_word_fill_field, tmp_path)


def test_addrspace_iter_fill_defaults(sparse_addrspace, tmp_path):
    """Iterate with filling."""
    _dump_addrspace(
        sparse_addrspace.iter(fill_word=create_fill_word, fill_field=create_fill_field),
        tmp_path,
    )
    assert_refdata(test_addrspace_iter_fill_defaults, tmp_path)


def test_zip():
    """Zip."""
    a0 = Addrspace(name="a0", baseaddr=0x0000, size=0x1000)
    a1 = Addrspace(name="a1", baseaddr=0x1000, size=0x1000)
    b0 = Addrspace(name="b0", baseaddr=0x0000, size=0x1000)
    b1 = Addrspace(name="b1", baseaddr=0x1000, size=0x800)
    b2 = Addrspace(name="b2", baseaddr=0x1800, size=0x800)

    assert tuple(zip_addrspaces((), (b0,))) == ()
    assert tuple(zip_addrspaces((a0, a1), (b0, b1))) == ((a0, b0), (a1, b1))
    assert tuple(zip_addrspaces((a0,), (b0,))) == ((a0, b0),)
    assert tuple(zip_addrspaces((a0, a1), (b0, b1, b2))) == ((a0, b0), (a1, b1), (a1, b2))


def test_ident():
    """Ident."""
    addrspace = Addrspace(name="name", width=32, depth=32)
    with raises(u.ValidationError):
        addrspace.add_word("foo ")

    word = addrspace.add_word("foo")
    with raises(u.ValidationError):
        word.add_field("foo ", type_=u.UintType(2))


def test_default_addrspace():
    """Default Address Space."""
    default = DefaultAddrspace(size="4kb", attrs="one")
    assert default.name == ""
    assert default.size == 4096
    assert default.attrs == (Attr("one"),)


ATTRS = (
    "one=two; foo=bar",
    {"one": "two", "foo": "bar"},
    (Attr(name="one", value="two"), Attr(name="foo", value="bar")),
)


@mark.parametrize("attrs", ATTRS)
def test_addrspace_attrs(attrs):
    """Test Attrs."""
    addrspace = Addrspace(size="4kb", attrs=attrs)
    assert addrspace.attrs == (Attr("one", value="two"), Attr(name="foo", value="bar"))


@mark.parametrize("attrs", ATTRS)
def test_word_attrs(attrs):
    """Test Attrs."""
    addrspace = Addrspace(size="4kb")
    word = addrspace.add_word(name="name", attrs=attrs)
    assert word.attrs == (Attr("one", value="two"), Attr(name="foo", value="bar"))


@mark.parametrize("attrs", ATTRS)
def test_field_attrs(attrs):
    """Test Attrs."""
    addrspace = Addrspace(size="4kb")
    word = addrspace.add_word(name="name")
    field = word.add_field("field", u.UintType(4), attrs=attrs)
    assert field.attrs == (Attr("one", value="two"), Attr(name="foo", value="bar"))


def test_add_words(tmp_path):
    """Iterate with field filling."""
    addrspace = Addrspace(name="module", width=32, depth=128)

    word = addrspace.add_words("a")
    a_a = word.add_field("a", u.UintType(14), "RW")
    a_b = word.add_field("b", u.UintType(14), "RW")
    a_c = word.add_field("c", u.UintType(14), "RW")
    a_d = word.add_field("d", u.UintType(14), "RW")
    assert tuple(w.name for w in word.words) == ("a0", "a1")
    assert word.fields == (a_a, a_b, a_c, a_d)

    word = addrspace.add_words("b", align=16, naming="dec1")
    b_a = word.add_field("a", u.UintType(14), "RW")
    b_b = word.add_field("b", u.UintType(18), "RW")
    b_c = word.add_field("c", u.UintType(10), "RW")
    b_d = word.add_field("d", u.UintType(23), "RW")
    assert tuple(w.name for w in word.words) == ("b1", "b2", "b3")
    assert word.fields == (b_a, b_b, b_c, b_d)

    _dump_addrspace(addrspace.iter(fill=True), tmp_path)
    assert_refdata(test_add_words, tmp_path)


def _mynaming(value: int) -> str:
    return chr(65 + value)


@mark.parametrize("naming", ("dec", "alpha", _mynaming))
def test_add_words_naming(tmp_path, naming):
    """Iterate with field filling."""
    addrspace = Addrspace(name="module", width=32, depth=128, add_words_naming=naming)

    word = addrspace.add_words("a")
    word.add_field("a", u.UintType(14), "RW")
    word.add_field("b", u.UintType(14), "RW")
    word.add_field("c", u.UintType(14), "RW")
    word.add_field("d", u.UintType(14), "RW")

    for name, wordnaming in (("b", "dec"), ("c", "alpha"), ("d", _mynaming)):
        word = addrspace.add_words(name, align=16, naming=wordnaming)
        word.add_field("a", u.UintType(14), "RW")
        word.add_field("b", u.UintType(18), "RW")
        word.add_field("c", u.UintType(10), "RW")
        word.add_field("d", u.UintType(23), "RW")

    flavor = "func" if naming is _mynaming else naming
    _dump_addrspace(addrspace.iter(), tmp_path)
    assert_refdata(test_add_words_naming, tmp_path, flavor=flavor)


class MyField(Field):
    """Example Field Implementation."""

    basename: str


class MyWord(Word):
    """Example Word Implementation."""

    def _create_field(self, **kwargs) -> Field:
        name = kwargs.pop("name")
        basename = kwargs.pop("basename", None) or f"{self.name}_{name}"
        return MyField(name=name, basename=basename, **kwargs)


class MyWords(Words):
    """Example Words Implementation."""

    def _add_field(self, name: str, type_: u.BaseScalarType, *args, **kwargs):
        basename = kwargs.pop("basename", None) or f"{self.name}_{name}"
        self.word.add_field(name, type_, *args, basename=basename, **kwargs)


class MyAddrspace(Addrspace):
    """Example Addrspace Implementation."""

    def _create_word(self, **kwargs) -> Word:
        return MyWord(**kwargs)

    def _create_words(self, **kwargs) -> Words:
        return MyWords.create(**kwargs)


def test_add_words_custom(tmp_path):
    """Iterate with field filling."""
    addrspace = MyAddrspace(name="module", width=32, depth=128)

    word = addrspace.add_words("a")
    word.add_field("a", u.UintType(14), "RW")
    word.add_field("b", u.UintType(14), "RW", basename="base")
    word.add_field("c", u.UintType(14), "RW")
    word.add_field("d", u.UintType(14), "RW")

    word = addrspace.add_words("b", align=16)
    word.add_field("a", u.UintType(14), "RW")
    word.add_field("b", u.UintType(18), "RW", basename="base")
    word.add_field("c", u.UintType(10), "RW")
    word.add_field("d", u.UintType(23), "RW")

    _dump_addrspace(addrspace.iter(), tmp_path)
    assert_refdata(test_add_words_custom, tmp_path)
