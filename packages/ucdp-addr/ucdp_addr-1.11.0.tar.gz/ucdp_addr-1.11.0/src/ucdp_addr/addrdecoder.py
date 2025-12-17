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

"""
Address Decoder aka Demultiplexer.
"""

from logging import getLogger

import ucdp as u

from .addrmap import AddrMap
from .addrmapfinder import get_addrspaces
from .addrref import AddrRef
from .addrspaces import Addrspaces, join_addrspaces
from .const import NOREF

LOGGER = getLogger(__name__)


class AddrDecoder(u.Object):
    """
    Address Decoder aka Demultiplexer.

    An address decoder manages the access to a known list of slaves.
    The address map contains the address to slave mapping.

    An address decoder contains a unique address map and a namespace with all slaves.
    """

    addrmap: AddrMap = u.Field(default_factory=lambda: AddrMap(unique=True))
    """Address Map With All Slaves."""

    slaves: u.Namespace = u.Field(default_factory=u.Namespace)
    """Namespace With All Slaves."""

    default_size: u.Bytes | None = None
    """Default Size if not given."""

    is_sub: bool = False
    """Just decode address LSBs."""

    def get_addrspaces(self, **kwargs) -> Addrspaces:
        """Address Spaces."""
        for addrspace in self.addrmap:
            ref = addrspace.slave.ref
            if ref is None:
                LOGGER.warning("%r: %r does not reference anything", self, addrspace)
                continue
            if ref is NOREF:
                continue
            ref = self._resolve_ref(ref)
            yield from join_addrspaces(addrspace, get_addrspaces(ref, kwargs))

    def _resolve_ref(self, ref: AddrRef) -> AddrRef:
        return ref
