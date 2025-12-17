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
"""Test Address Decoder."""

import re

import ucdp as u
from pytest import raises
from test2ref import assert_refdata

from ucdp_addr import NOREF, AddrDecoder, AddrMap, AddrSlave, Addrspace, Addrspaces


class Mod(u.AMod):
    """Just a module."""

    def _build(self) -> None:
        pass

    def get_addrspaces(self, master=None, **kwargs) -> Addrspaces:
        """Address Spaces."""
        addrspace = Addrspace(name=self.hiername, width=32, depth=64)
        addrspace.add_word("one")
        if not master:
            addrspace.add_word("two", offset=7)
        yield addrspace


def test_basic(tmp_path, caplog):
    """Address Decoder Basics."""
    decoder = AddrDecoder()
    assert tuple(decoder.addrmap) == ()
    assert tuple(decoder.slaves) == ()
    assert decoder.default_size is None
    assert decoder.is_sub is False

    onemod = Mod(name="one")
    othermod = Mod(name="other")

    one = AddrSlave(name="one", addrdecoder=decoder, ref=onemod)
    decoder.slaves.add(one)

    other = AddrSlave(name="other", addrdecoder=decoder, ref=othermod)
    decoder.slaves.add(other)

    noaddr = AddrSlave(name="noaddr", addrdecoder=decoder)
    decoder.slaves.add(noaddr)

    empty = AddrSlave(name="empty", addrdecoder=decoder)
    decoder.slaves.add(empty)

    nomod = AddrSlave(name="nomod", addrdecoder=decoder, ref=NOREF)
    decoder.slaves.add(nomod)

    assert tuple(decoder.addrmap) == ()
    assert tuple(decoder.slaves) == (one, other, noaddr, empty, nomod)

    addrspaces = (
        one.add_addrrange(size="2k"),
        other.add_addrrange(size="4k"),
        empty.add_addrrange(size="1k"),
        one.add_addrrange(size="2k"),
        nomod.add_addrrange(size="1k"),
        other.add_addrrange(size="4k"),
    )

    assert tuple(decoder.addrmap) == addrspaces
    assert tuple(decoder.slaves) == (one, other, noaddr, empty, nomod)

    resolved = AddrMap.from_addrspaces(decoder.get_addrspaces())

    (tmp_path / "addrmap.md").write_text(decoder.addrmap.get_overview())
    (tmp_path / "resolved.md").write_text(resolved.get_overview())
    assert_refdata(test_basic, tmp_path, caplog=caplog)


def test_addrrange():
    """Test Address Range."""
    decoder = AddrDecoder(default_size="5k")

    one = AddrSlave(name="one", addrdecoder=decoder)
    decoder.slaves.add(one)
    addrspace = one.add_addrrange()
    assert addrspace.size == 5 * 1024

    two = AddrSlave(name="two", addrdecoder=decoder)
    msg = "baseaddr 7168 is not aligned to size 4096"
    with raises(ValueError, match=re.escape(msg)):
        two.add_addrrange(baseaddr=7 * 1024, size=4 * 1024)
