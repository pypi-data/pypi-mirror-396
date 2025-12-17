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
from pytest import raises
from test2ref import assert_refdata

from ucdp_addr import get_addrmap


def test_find_top(tmp_path, testdata_path):
    """Test Find on Example Top Module."""
    mod = u.load("top_lib.top.TopMod").mod
    addrmap = get_addrmap(mod)

    (tmp_path / "overview.md").write_text(addrmap.get_overview())
    assert_refdata(test_find_top, tmp_path)


def test_find_multiple(testdata_path):
    """Multiple."""
    mod = u.load("top_lib.top.SubMod").mod
    msg = (
        "Multiple modules implement 'get_addrspaces':\n"
        "  <top_lib.top.BusMod(inst='sub/u_bus', libname='top_lib', modname='bus')>\n"
        "  <top_lib.top.BusMod(inst='sub/u_otherbus', libname='top_lib', modname='bus')>\n"
        "Implement 'get_addrspaces' on a parent module or choose a different top."
    )
    with raises(ValueError, match=re.escape(msg)):
        get_addrmap(mod)


def test_none(testdata_path):
    """No implementation."""
    mod = u.load("top_lib.top.EmptyMod").mod
    msg = "No module found which implements 'get_addrspaces'"
    with raises(ValueError, match=re.escape(msg)):
        get_addrmap(mod)
