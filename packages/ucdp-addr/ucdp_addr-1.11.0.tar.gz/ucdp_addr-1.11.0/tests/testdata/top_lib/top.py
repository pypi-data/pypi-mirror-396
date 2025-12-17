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

import ucdp as u

from ucdp_addr import AddrMap, Addrspace, Addrspaces, join_addrspaces


class TopMod(u.AMod):
    """Example Top Module."""

    def _build(self):
        SubMod(self, "u_sub0")
        SubMod(self, "u_sub1")

    def get_addrspaces(self, **kwargs) -> Addrspaces:
        """Determine Address Spaces."""
        base = Addrspace(name="main0", baseaddr=0x10000, size=0x10000, is_sub=False)
        yield from join_addrspaces(base, self.get_inst("u_sub0/u_bus").get_addrspaces(**kwargs))

        base = Addrspace(name="main1", baseaddr=0x40000, size=0x10000, is_sub=False)
        yield from join_addrspaces(base, self.get_inst("u_sub1/u_bus").get_addrspaces(**kwargs))


class SubMod(u.AMod):
    """Example Sub Module."""

    def _build(self):
        BusMod(self, "u_bus")
        BusMod(self, "u_otherbus")


class BusMod(u.AMod):
    """Bus Module."""

    addrmap: AddrMap = u.Field(default_factory=AddrMap)

    def _build(self):
        addrspace = Addrspace(name="one", baseaddr=0x1000, size="2KB")
        self.addrmap.add(addrspace)
        word = addrspace.add_word("word0", offset=4)
        word.add_field("field0", u.UintType(4), "RW")

        addrspace = Addrspace(name="two", baseaddr=0x2000, size="4KB")
        self.addrmap.add(addrspace)
        word = addrspace.add_word("word1", offset=0x3F0)
        word.add_field("field1", u.UintType(32), "RO")

    def get_addrspaces(self, master=None, **kwargs) -> Addrspaces:
        """Address Spaces."""
        for addrspace in self.addrmap:
            if master and addrspace.name == "two":
                continue
            yield addrspace


class EmptyMod(u.AMod):
    """No get_addrspaces implementation."""

    def _build(self):
        pass
