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

from test2ref import assert_refdata

from ucdp_addr import AddrMaster, AddrMatrix, AddrSlave


def test_basic(tmp_path, caplog):
    """Basics."""
    matrix = AddrMatrix()
    assert tuple(matrix.masters) == ()
    assert tuple(matrix.slaves) == ()

    (tmp_path / "overview.md").write_text(matrix.get_overview())
    matrix._check_masters_slaves()
    assert_refdata(test_basic, tmp_path, caplog=caplog)


def test_example(tmp_path, caplog):
    """Example."""
    matrix = AddrMatrix()
    mext = AddrMaster(name="ext")
    mdsp = AddrMaster(name="dsp")

    matrix._add_master(mext)
    matrix._add_master(mdsp)

    sram = AddrSlave(name="ram", addrdecoder=matrix)
    speriph = AddrSlave(name="periph", addrdecoder=matrix)
    smisc = AddrSlave(name="misc", addrdecoder=matrix)

    matrix._add_slave(sram, masternames=["ext", "dsp"], baseaddr=0xF000_0000, size=2**16)
    matrix._add_slave(speriph, masternames="dsp", size="32kB")
    matrix._add_slave(smisc, masternames="ext", size="64kB")

    matrix.add_interconnects("dsp", "periph")
    matrix.add_interconnects("ext", "misc")

    assert tuple(matrix.masters) == (mext, mdsp)
    assert tuple(matrix.slaves) == (sram, speriph, smisc)

    (tmp_path / "overview.md").write_text(matrix.get_overview())
    matrix._check_masters_slaves()
    assert_refdata(test_example, tmp_path, caplog=caplog)


def test_corner(tmp_path, caplog):
    """Some Cornercases."""
    matrix = AddrMatrix()
    matrix._add_master(AddrMaster(name="mst"))
    matrix._add_slave(AddrSlave(name="slv", addrdecoder=matrix))
    matrix.add_interconnects("foo", "bar")

    (tmp_path / "overview.md").write_text(matrix.get_overview())
    matrix._check_masters_slaves()
    assert_refdata(test_corner, tmp_path, caplog=caplog)
