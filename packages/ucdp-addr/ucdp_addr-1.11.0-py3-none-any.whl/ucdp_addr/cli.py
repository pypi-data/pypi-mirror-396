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

"""Command Line Interface."""

import click
from ucdp import cli

from .addrmapfinder import get_addrmap

opt_addrdefine = click.option(
    "--addrdefine",
    "-A",
    multiple=True,
    type=str,
    help="Address Defines for Address Map. Environment Variable 'UCDP_ADDRDEFINES'",
    envvar="UCDP_ADDRDEFINES",
)


@click.command(
    help=f"""
Load Data Model and List Address Map.

TOP: Top Module. {cli.PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'
"""
)
@cli.arg_top
@cli.opt_path
@click.option("--full", "-f", is_flag=True)
@opt_addrdefine
@cli.opt_file
@cli.pass_ctx
def lsaddrmap(ctx, top, path, full, addrdefine=None, file=None):
    """Load Data Model and List Address Map."""
    top = cli.load_top(ctx, top, path, quiet=True)
    defines = cli.defines2data(addrdefine)
    addrmap = get_addrmap(top.mod, defines=defines, ref=top.ref)
    print(addrmap.get_overview(minimal=not full), end="", file=file)
