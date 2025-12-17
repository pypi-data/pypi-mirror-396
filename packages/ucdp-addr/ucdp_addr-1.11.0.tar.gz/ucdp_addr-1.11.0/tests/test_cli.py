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
"""Test Command-Line-Interface."""

import ucdp as u
from click.testing import CliRunner
from pytest import fixture
from test2ref import assert_refdata


@fixture
def runner():
    """Click Runner for Testing."""
    yield CliRunner()


def _run(runner, path, cmd):
    result = runner.invoke(u.cli.ucdp, cmd)
    assert result.exit_code == 0
    (path / "console.md").write_text(result.output)


def test_lsaddrmap(runner, tmp_path, testdata_path):
    """Lsaddrmap Command."""
    _run(runner, tmp_path, ["lsaddrmap", "top_lib.top"])
    assert_refdata(test_lsaddrmap, tmp_path)


def test_lsaddrmap_full(runner, tmp_path, testdata_path):
    """Lsaddrmap Command Full with File."""
    _run(runner, tmp_path, ["lsaddrmap", "top_lib.top", "--full"])
    assert_refdata(test_lsaddrmap_full, tmp_path)


def test_lsaddrmap_full_file(runner, tmp_path, testdata_path):
    """Lsaddrmap Command."""
    filepath = tmp_path / "file.md"
    _run(runner, tmp_path, ["lsaddrmap", "top_lib.top", "--full", "--file", str(filepath)])
    assert_refdata(test_lsaddrmap_full_file, tmp_path)


def test_lsaddrmap_full_define_one(runner, tmp_path, testdata_path):
    """Lsaddrmap Command."""
    _run(runner, tmp_path, ["lsaddrmap", "top_lib.top", "--full", "-A", "one=two"])
    assert_refdata(test_lsaddrmap_full_define_one, tmp_path)


def test_lsaddrmap_full_define_master(runner, tmp_path, testdata_path):
    """Lsaddrmap Command."""
    _run(runner, tmp_path, ["lsaddrmap", "top_lib.top", "--full", "-A", "master=apps"])
    assert_refdata(test_lsaddrmap_full_define_master, tmp_path)
