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

import ucdp_addr as ua


@fixture
def addrmap():
    """Alias to one."""
    addrmap = ua.AddrMap()
    for idx, aname in enumerate(("uart", "spi", "owi")):
        addrspace = ua.Addrspace(name=aname, width=32, depth=8, baseaddr=8 * 4 * idx)
        addrmap.add(addrspace)
        word = addrspace.add_word("ctrl")
        word.add_field("ena", u.EnaType(), "RW")
        word.add_field("mode", u.UintType(4, default=1), "RW")
        word.add_field("speed", u.UintType(8, default=3), "RW")
        word = addrspace.add_word("stat")
        word.add_field("bsy", u.BitType(), "RO", offset=9)
        word = addrspace.add_word("rc")
        word.add_field("bit", u.BitType(), "RC")
        word = addrspace.add_word("wl")
        word.add_field("bit", u.BitType(), "WL")
    return addrmap


def test_int(addrmap):
    """Integer."""
    item = 0x20

    wordinfo = ua.WordInfo.create(addrmap, item, 5)
    assert str(wordinfo) == "0x20 [0x20 1x32 (4 bytes)] SINGLE: 5"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x20'), 5),)"

    wordinfo = ua.WordInfo.create(addrmap, item, (5, 6))
    assert str(wordinfo) == "0x20 [0x20 2x32 (8 bytes)] BURST: (5, 6)"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x20'), 5), (Hex('0x24'), 6))"

    wordinfo = ua.WordInfo.create(addrmap, item, ((8, 5), (16, 6)))
    assert str(wordinfo) == "0x20 [0x20 5x32 (20 bytes)] SCAT: ((8, 5), (16, 6))"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x28'), 5), (Hex('0x30'), 6))"

    wordinfo = ua.WordInfo.create(addrmap, item, 5, mask=0xF, offset=8)
    assert str(wordinfo) == "0x28 [0x28 1x32 (4 bytes)] mask=0xF SINGLE: 5"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x28'), 5),)"


def test_addrrange(addrmap):
    """Address Range."""
    item = ua.AddrRange(baseaddr=0x20, size=64)

    wordinfo = ua.WordInfo.create(addrmap, item, 5)
    assert str(wordinfo) == "0x20 [0x20 1x32 (4 bytes)] SINGLE: 5"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x20'), 5),)"

    wordinfo = ua.WordInfo.create(addrmap, item, (5, 6))
    assert str(wordinfo) == "0x20 [0x20 2x32 (8 bytes)] BURST: (5, 6)"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x20'), 5), (Hex('0x24'), 6))"
    assert str(tuple(wordinfo.addrs())) == "(Hex('0x20'), Hex('0x24'))"

    wordinfo = ua.WordInfo.create(addrmap, item, ((8, 5), (16, 6)))
    assert str(wordinfo) == "0x20 [0x20 5x32 (20 bytes)] SCAT: ((8, 5), (16, 6))"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x28'), 5), (Hex('0x30'), 6))"
    assert str(tuple(wordinfo.addrs())) == "(Hex('0x28'), Hex('0x30'))"

    wordinfo = ua.WordInfo.create(addrmap, item, 5, mask=0xF, offset=8)
    assert str(wordinfo) == "0x20 [0x28 1x32 (4 bytes)] mask=0xF SINGLE: 5"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x28'), 5),)"


def test_addrspace(addrmap):
    """Address Space."""
    wordinfo = ua.WordInfo.create(addrmap, "spi", 5)
    assert str(wordinfo) == "spi [0x20 1x32 (4 bytes)] SINGLE: 5"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x20'), 5),)"

    wordinfo = ua.WordInfo.create(addrmap, "spi", (5, 6))
    assert str(wordinfo) == "spi [0x20 2x32 (8 bytes)] BURST: (5, 6)"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x20'), 5), (Hex('0x24'), 6))"

    wordinfo = ua.WordInfo.create(addrmap, "spi", ((8, 5), (16, 6)))
    assert str(wordinfo) == "spi [0x20 5x32 (20 bytes)] SCAT: ((8, 5), (16, 6))"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x28'), 5), (Hex('0x30'), 6))"

    wordinfo = ua.WordInfo.create(addrmap, "spi", 5, mask=0xF, offset=8)
    assert str(wordinfo) == "spi [0x28 1x32 (4 bytes)] mask=0xF SINGLE: 5"
    assert str(tuple(wordinfo.iter())) == "((Hex('0x28'), 5),)"

    with raises(ValueError, match=re.escape("offset=32 exceeds size (32 bytes)")):
        ua.WordInfo.create(addrmap, "spi", 5, offset=32)

    with raises(ValueError, match=re.escape("data size 128 exceeds size (32 bytes)")):
        ua.WordInfo.create(addrmap, "spi", tuple(range(32)))

    with raises(ValueError, match=re.escape("'wordsize' is forbidden for non integer")):
        ua.WordInfo.create(addrmap, "spi", 5, wordsize=8)


def test_word(addrmap):
    """Word."""
    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl", "ena=ena")
    assert str(wordinfo) == "spi.ctrl [0x20 1x32 (4 bytes)] mask=0x1 RMW SINGLE: 1"

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl", "ena=ena, mode=9")
    assert str(wordinfo) == "spi.ctrl [0x20 1x32 (4 bytes)] mask=0x1F RMW SINGLE: 19"

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl", "ena=ena, mode=9, speed=0x14")
    assert str(wordinfo) == "spi.ctrl [0x20 1x32 (4 bytes)] mask=0x1FFF SINGLE: 659"

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl", "ena=ena, *=2")
    assert str(wordinfo) == "spi.ctrl [0x20 1x32 (4 bytes)] mask=0x1FFF SINGLE: 69"

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl", "*=<RST>")
    assert str(wordinfo) == "spi.ctrl [0x20 1x32 (4 bytes)] mask=0x1FFF SINGLE: 98"

    wordinfo = ua.WordInfo.create(addrmap, "spi.rc", "bit=1")
    assert str(wordinfo) == "spi.rc [0x28 1x32 (4 bytes)] mask=0x1 !R SINGLE: 1"

    wordinfo = ua.WordInfo.create(addrmap, "spi.wl", "bit=1")
    assert str(wordinfo) == "spi.wl [0x2C 1x32 (4 bytes)] mask=0x1 !W SINGLE: 1"

    with raises(ValueError, match=re.escape("Value 'disenabled' is not covered by EnaType()")):
        ua.WordInfo.create(addrmap, "spi.ctrl", "ena=disenabled")

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl", {"ena": 1})
    assert str(wordinfo) == "spi.ctrl [0x20 1x32 (4 bytes)] mask=0x1 RMW SINGLE: 1"

    with raises(TypeError, match=re.escape("'data' must be 'int', 'str' or 'dict' for fields, not (1, 2)")):
        ua.WordInfo.create(addrmap, "spi.ctrl", (1, 2))

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl", 8)
    assert str(wordinfo) == "spi.ctrl [0x20 1x32 (4 bytes)] SINGLE: 8"

    with raises(ValueError, match=re.escape("Unknown field names: 'foo', 'bar'")):
        ua.WordInfo.create(addrmap, "spi.ctrl", {"ena": 1, "foo": 3, "bar": 5})


def test_field(addrmap):
    """Field."""
    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl.ena", "ena")
    assert str(wordinfo) == "spi.ctrl.ena [0x20 1x32 (4 bytes)] mask=0x1 RMW SINGLE: 1"

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl.ena", "dis")
    assert str(wordinfo) == "spi.ctrl.ena [0x20 1x32 (4 bytes)] mask=0x1 RMW SINGLE: 0"

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl.ena", 1)
    assert str(wordinfo) == "spi.ctrl.ena [0x20 1x32 (4 bytes)] mask=0x1 RMW SINGLE: 1"

    wordinfo = ua.WordInfo.create(addrmap, "spi.ctrl.mode", 9)
    assert str(wordinfo) == "spi.ctrl.mode [0x20 1x32 (4 bytes)] mask=0x1E RMW SINGLE: 18"

    with raises(ValueError, match=re.escape("'offset' is not allowed for words and fields")):
        ua.WordInfo.create(addrmap, "spi.ctrl.mode", 5, offset=32)

    with raises(ValueError, match=re.escape("'mask' is not allowed for fields")):
        ua.WordInfo.create(addrmap, "spi.ctrl.mode", 5, mask=31)

    with raises(TypeError, match=re.escape("'data' must be 'int' or 'str' for fields, not (5, 6)")):
        ua.WordInfo.create(addrmap, "spi.ctrl.mode", (5, 6))

    with raises(TypeError, match=re.escape("'data' must be 'int' or 'str' for fields, not ((8, 5), (16, 6))")):
        ua.WordInfo.create(addrmap, "spi.ctrl.mode", ((8, 5), (16, 6)))
