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
Master-Slave Matrix.
"""

from collections import defaultdict
from logging import getLogger

import aligntext
import ucdp as u

from .addrdecoder import AddrDecoder
from .addrmaster import AddrMaster
from .addrslave import AddrSlave

LOGGER = getLogger(__name__)


class AddrMatrix(AddrDecoder):
    """
    Bus Matrix with a number of masters and slave with optional connections.
    """

    masters: u.Namespace = u.Field(default_factory=u.Namespace)
    """Masters."""

    _master_slaves = u.PrivateField(default_factory=lambda: defaultdict(list))
    _slave_masters = u.PrivateField(default_factory=lambda: defaultdict(list))

    def _add_master(
        self,
        master: AddrMaster,
        slavenames: u.Names | None = None,
    ):
        self._check_lock()
        self.masters.add(master)
        self.add_interconnects((master.name,), slavenames)

    def _add_slave(
        self,
        slave: AddrSlave,
        masternames: u.Names | None = None,
        baseaddr=u.AUTO,
        size: u.Bytes | None = None,
    ):
        self._check_lock()
        self.slaves.add(slave)
        if baseaddr is not None and (size is not None or self.default_size):
            slave.add_addrrange(baseaddr, size)
        self.add_interconnects(masternames, (slave.name,))

    def add_interconnects(self, masternames: u.Names, slavenames: u.Names):
        """Add Interconnects."""
        self._check_lock()
        for mastername in u.split(masternames):
            for slavename in u.split(slavenames):
                if slavename in self._master_slaves[mastername]:
                    LOGGER.warning("%s: interconnect %s -> %s already exists", self, mastername, slavename)
                    continue
                self._master_slaves[mastername].append(slavename)
                self._slave_masters[slavename].append(mastername)

    @property
    def master_slaves(self) -> tuple[tuple[AddrMaster, tuple[AddrSlave, ...]], ...]:
        """Masters and Their Slaves."""
        pairs: list[tuple[AddrMaster, tuple[AddrSlave, ...]]] = []
        slaves = self.slaves
        for master in self.masters:
            slavenames = self._master_slaves[master.name]
            masterslaves = tuple(slaves[name] for name in slavenames if name in slaves)
            pairs.append((master, masterslaves))
        return tuple(pairs)

    @property
    def slave_masters(self) -> tuple[tuple[AddrSlave, tuple[AddrMaster, ...]], ...]:
        """Slaves and Their Masters."""
        pairs: list[tuple[AddrSlave, tuple[AddrMaster, ...]]] = []
        masters = self.masters
        for slave in self.slaves:
            masternames = self._slave_masters[slave.name]
            masters = tuple(masters[name] for name in masternames if name in masters)
            pairs.append((slave, masters))
        return tuple(pairs)

    def _check_lock(self):
        """Check Lock."""

    def _check_masters_slaves(self):
        """Run Consistency Checks."""
        masters = self.masters
        slaves = self.slaves
        if not masters:
            LOGGER.warning("%s has no masters", self)
        if not slaves:
            LOGGER.warning("%s has no slaves", self)
        for master, slaves in self.master_slaves:
            if not slaves:
                LOGGER.warning("%s: %r has no slaves", self, master)
        for slave, masters in self.slave_masters:
            if not masters:
                LOGGER.warning("%s: %r has no masters", self, slave)
        for unknown_master in set(self._master_slaves.keys()) - set(self.masters.keys()):
            LOGGER.warning("Master %r is not known", unknown_master)
        for unknown_slave in set(self._slave_masters.keys()) - set(self.slaves.keys()):
            LOGGER.warning("Slaves %r is not known", unknown_slave)

    def get_overview(self):
        """Return overview tables."""
        overview = [
            self._get_overview_matrix(),
            self.addrmap.get_overview(minimal=True, fill=True),
        ]
        return "\n\n\n".join(overview)

    def _get_overview_matrix(self) -> str:
        def align(data) -> str:
            lines = list(data)
            lens = (max(len(cell) for cell in row) for row in zip(*lines, strict=False))
            lines.insert(1, ("-" * len_ for len_ in lens))
            return aligntext.align(lines, seps=(" | ",), sepfirst="| ", seplast=" |") + "\n"

        slaves = self.slaves
        headers = ["Master > Slave"] + [slave.name for slave in slaves]
        matrix = [headers]
        idxmap = {slave.name: idx for idx, slave in enumerate(slaves, 1)}
        empty = ["" for slave in slaves]
        for master, slaves in self.master_slaves:
            item = [master.name, *empty]
            for slave in slaves:
                item[idxmap[slave.name]] = "X"
            matrix.append(item)

        return align(matrix)
