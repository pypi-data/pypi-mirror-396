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

from ucdp_addr import Addrspace, AddrspaceAlias


def test_alias():
    """Test Alias."""
    addrspace = Addrspace(name="a", size="1KB")
    word0 = addrspace.add_word("word0")

    alias = AddrspaceAlias(addrspace=addrspace)
    other_alias = AddrspaceAlias(addrspace=addrspace, name="foo")

    word1 = addrspace.add_word("word1")

    assert addrspace.name == "a"
    assert alias.name == "a_alias"
    assert other_alias.name == "foo"
    assert tuple(addrspace.words) == (word0, word1)
    assert tuple(alias.words) == (word0, word1)
    assert tuple(other_alias.words) == (word0, word1)
