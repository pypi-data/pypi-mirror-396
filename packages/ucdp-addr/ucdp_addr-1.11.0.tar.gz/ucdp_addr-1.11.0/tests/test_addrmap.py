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
from pytest import fixture, raises
from test2ref import assert_refdata

from ucdp_addr import AddrMap, Addrspace, AddrspaceAlias, create_fill_addrspace


@fixture
def zero():
    """Zero."""
    return Addrspace(name="zero", baseaddr=0x0000, size=0x1000)


@fixture
def one():
    """One."""
    addrspace = Addrspace(name="one", baseaddr=0x1000, size=0x1000, is_volatile=True, attrs="a=1;b")
    word = addrspace.add_word("word0")
    word.add_field("field", u.UintType(3), "RW", attrs="foo")
    word = addrspace.add_word("word1", depth=4, attrs="bar=4")
    word.add_field("field", u.UintType(3), "RW")
    return addrspace


@fixture
def two():
    """Two."""
    addrspace = Addrspace(name="two", baseaddr=0x3000, size=0x1000)
    word = addrspace.add_word("word", offset=8)
    word.add_field("field", u.UintType(3), "RW", offset=6)
    return addrspace


@fixture
def three():
    """Three."""
    return Addrspace(name="three", baseaddr=0x7F000000, size=0x1000, is_sub=False)


@fixture
def four():
    """Four."""
    # Overlapping with two at the end
    return Addrspace(name="four", baseaddr=0x3800, size=0x800)


@fixture
def five():
    """Five."""
    # Overlapping with two at the start
    return Addrspace(name="five", baseaddr=0x2E00, size=0x400)


@fixture
def alias(one):
    """Alias to one."""
    return AddrspaceAlias(one, baseaddr=0x6000)


def test_empty(tmp_path):
    """Empty Address Map."""
    addrmap = AddrMap()
    assert repr(addrmap) == "AddrMap()"

    assert addrmap.size is None
    assert addrmap.addrwidth is None
    assert addrmap.firstaddr is None
    assert addrmap.lastaddr is None
    assert addrmap.addrslice is None

    (tmp_path / "overview.md").write_text(addrmap.get_overview())
    assert_refdata(test_empty, tmp_path)


def test_growing(tmp_path, one, two, three, four, alias):
    """Growing Address Map."""
    addrmap = AddrMap()
    assert repr(addrmap) == "AddrMap()"

    addrmap.add(one)
    assert repr(addrmap.size) == "Bytesize('8 KB')"
    assert addrmap.addrwidth == 13
    assert addrmap.addrslice.bits == "12"
    assert repr(addrmap.firstaddr) == "Hex('0x1000')"
    assert repr(addrmap.lastaddr) == "Hex('0x1FFF')"

    addrmap.add(two)
    assert repr(addrmap.size) == "Bytesize('16 KB')"
    assert addrmap.addrwidth == 14
    assert addrmap.addrslice.bits == "13:12"
    assert repr(addrmap.firstaddr) == "Hex('0x1000')"
    assert repr(addrmap.lastaddr) == "Hex('0x3FFF')"

    addrmap.add(three)
    assert repr(addrmap.size) == "Bytesize('2080772 KB')"
    assert addrmap.addrwidth == 31
    assert addrmap.addrslice.bits == "30:12"
    assert repr(addrmap.firstaddr) == "Hex('0x1000')"
    assert repr(addrmap.lastaddr) == "Hex('0x7F000FFF')"

    addrmap.add(alias)
    addrmap.add(four)

    assert tuple(addrmap) == (one, two, four, alias, three)
    assert tuple(addrmap.iter()) == (one, two, four, alias, three)
    assert tuple(addrmap.iter(filter_=lambda addrspace: addrspace.name != "two")) == (one, four, alias, three)

    with (tmp_path / "iter-fillfunc.txt").open("w") as file:
        for item in addrmap.iter(fill=create_fill_addrspace):
            file.write(f"{item!r}\n")

    with (tmp_path / "iter-filltrue.txt").open("w") as file:
        for item in addrmap.iter(fill=True):
            file.write(f"{item!r}\n")

    with (tmp_path / "iter-fill-filter.txt").open("w") as file:
        for item in addrmap.iter(fill=True, filter_=lambda addrspace: addrspace.name != "two"):
            file.write(f"{item!r}\n")

    (tmp_path / "overview.md").write_text(addrmap.get_overview())
    assert_refdata(test_growing, tmp_path)


def test_fixed_size(tmp_path, one, two, three, alias):
    """Growing Address Map."""
    addrmap = AddrMap(fixed_size=0xF0000)
    assert repr(addrmap) == "AddrMap(fixed_size=Bytesize('960 KB'))"

    assert repr(addrmap.size) == "Bytesize('960 KB')"
    assert addrmap.addrwidth == 20
    assert addrmap.addrslice is None
    assert addrmap.firstaddr is None
    assert addrmap.lastaddr is None

    addrmap.add(one)
    assert repr(addrmap.size) == "Bytesize('960 KB')"
    assert addrmap.addrwidth == 20
    assert addrmap.addrslice.bits == "19:12"
    assert repr(addrmap.firstaddr) == "Hex('0x1000')"
    assert repr(addrmap.lastaddr) == "Hex('0x1FFF')"

    addrmap.add(two)
    assert repr(addrmap.size) == "Bytesize('960 KB')"
    assert addrmap.addrwidth == 20
    assert addrmap.addrslice.bits == "19:12"
    assert repr(addrmap.firstaddr) == "Hex('0x1000')"
    assert repr(addrmap.lastaddr) == "Hex('0x3FFF')"

    msg = "size=Bytesize('4 KB'), is_sub=False): exceeds maximum size: 960 KB."
    with raises(ValueError, match=re.escape(msg)):
        addrmap.add(three)
    assert repr(addrmap.size) == "Bytesize('960 KB')"
    assert addrmap.addrwidth == 20
    assert addrmap.addrslice.bits == "19:12"
    assert repr(addrmap.firstaddr) == "Hex('0x1000')"
    assert repr(addrmap.lastaddr) == "Hex('0x3FFF')"

    addrmap.add(alias)

    assert tuple(addrmap) == (one, two, alias)

    (tmp_path / "overview.md").write_text(addrmap.get_overview())
    assert_refdata(test_fixed_size, tmp_path)


def test_unique(tmp_path, one, two, three, four, five):
    """Unique Address Map."""
    addrmap = AddrMap(unique=True)
    addrmap.add(one)
    addrmap.add(two)
    addrmap.add(three)

    msg = "size=Bytesize('2 KB')) overlaps with Addrspace(name='two',"
    with raises(ValueError, match=re.escape(msg)):
        addrmap.add(four)

    msg = "size=Bytesize('1 KB')) overlaps with Addrspace(name='two', baseaddr=Hex('0x3000')"
    with raises(ValueError, match=re.escape(msg)):
        addrmap.add(five)

    (tmp_path / "overview.md").write_text(addrmap.get_overview())
    assert_refdata(test_unique, tmp_path)


def test_corner(tmp_path, zero, one):
    """Corner Case."""
    addrmap = AddrMap()
    addrmap.add(zero)
    assert addrmap.addrslice.bits == "12"
    addrmap.add(one)
    assert addrmap.addrslice.bits == "12"

    (tmp_path / "overview.md").write_text(addrmap.get_overview())
    assert_refdata(test_corner, tmp_path)


def test_get_free_baseaddr(tmp_path, one, two, three):
    """Test Get Free Base Address."""
    addrmap = AddrMap(fixed_size=0x8000)

    # empty
    assert addrmap.get_free_baseaddr(1) == 0
    assert addrmap.get_free_baseaddr(0x1000) == 0
    assert addrmap.get_free_baseaddr(0x1000, align=0x2000) == 0
    assert addrmap.get_free_baseaddr(0x1000, align=0x2000, start=0x800) == 0x2000
    assert addrmap.get_free_baseaddr(0x1000, align=0x2000, start=0x3000) == 0x4000
    assert addrmap.get_free_baseaddr(0x1000, align=0x2000, start=0x4000) == 0x4000
    assert addrmap.get_free_baseaddr(0x1000, start=0x800) == 0x1000
    assert addrmap.get_free_baseaddr(0x1000, start=0x3000) == 0x3000

    # one element
    addrmap.add(one)

    assert addrmap.get_free_baseaddr(1) == 0x2000
    assert addrmap.get_free_baseaddr(0x1000) == 0x2000
    assert addrmap.get_free_baseaddr(0x1000, align=0x800) == 0x2000
    assert addrmap.get_free_baseaddr(0x1000, align=0x800, start=0x800) == 0x2000
    assert addrmap.get_free_baseaddr(0x1000, align=0x800, start=0x3000) == 0x3000
    assert addrmap.get_free_baseaddr(0x1000, align=0x800, start=0x4000) == 0x4000
    assert addrmap.get_free_baseaddr(0x1000, start=0x800) == 0x2000
    assert addrmap.get_free_baseaddr(0x1000, start=0x3000) == 0x3000

    # second element
    addrmap.add(two)

    assert addrmap.get_free_baseaddr(1) == 0x4000
    assert addrmap.get_free_baseaddr(0x1000) == 0x4000
    assert addrmap.get_free_baseaddr(0x1000, align=0x800) == 0x4000
    assert addrmap.get_free_baseaddr(0x1000, align=0x800, start=0x800) == 0x2000
    assert addrmap.get_free_baseaddr(0x1000, align=0x800, start=0x3000) == 0x4000
    assert addrmap.get_free_baseaddr(0x1000, align=0x800, start=0x4000) == 0x4000
    assert addrmap.get_free_baseaddr(0x1000, start=0x800) == 0x2000

    msg = "End address 0x9000 would exceed maximum size 0x8000 (32 KB)"
    with raises(ValueError, match=re.escape(msg)):
        addrmap.get_free_baseaddr(0x1000, start=0x8000)
