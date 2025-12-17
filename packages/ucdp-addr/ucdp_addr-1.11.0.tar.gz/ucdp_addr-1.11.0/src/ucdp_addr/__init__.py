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
"""Unified Chip Design Platform - Address Map."""

from .access import (
    ACCESSES,
    NA,
    RC,
    RO,
    RP,
    RS,
    RT,
    RW,
    RW0C,
    RW0S,
    RW1C,
    RW1S,
    RWL,
    W0C,
    W0S,
    W1C,
    W1S,
    WL,
    WO,
    Access,
    ReadOp,
    ToAccess,
    WriteOp,
    any_read,
    cast_access,
    get_counteraccess,
    is_read_repeatable,
    is_write_repeatable,
)
from .addrdecoder import AddrDecoder
from .addrinfo import AddrInfo, Depth, Size
from .addrmap import AddrMap, AddrspaceFilter, FillAddrspaceFactory, create_fill_addrspace
from .addrmapfinder import GetAttrspacesFunc, get_addrmap, get_addrspaces
from .addrmapref import AddrMapRef, ToAddrMapRef
from .addrmaster import AddrMaster
from .addrmatrix import AddrMatrix
from .addrrange import AddrRange
from .addrref import AddrRef
from .addrslave import AddrSlave, SlaveAddrspace
from .addrspace import (
    Addrspace,
    DefaultAddrspace,
    Field,
    FieldFilter,
    FillFieldFactory,
    FillWordFactory,
    FullError,
    NamingScheme,
    ReservedAddrspace,
    Word,
    WordFields,
    WordFilter,
    Words,
    create_fill_field,
    create_fill_word,
    get_is_const,
    get_is_volatile,
    get_mask,
    name_alpha,
    read_on_modify,
    resolve_field_value,
)
from .addrspacealias import AddrspaceAlias
from .addrspaces import Addrspaces, join_addrspaces, zip_addrspaces
from .const import NOREF
from .data import DataType, check_data, get_datatype, get_size
from .datainfo import AddrData, DataInfo
from .defines import Defines
from .resolver import resolve, resolves
from .util import calc_depth_size, split_keyvaluepairs
from .wordinfo import WordInfo

__all__ = [
    "ACCESSES",
    "NA",
    "NOREF",
    "RC",
    "RO",
    "RP",
    "RS",
    "RT",
    "RW",
    "RW0C",
    "RW0S",
    "RW1C",
    "RW1S",
    "RWL",
    "W0C",
    "W0S",
    "W1C",
    "W1S",
    "WL",
    "WO",
    "Access",
    "AddrData",
    "AddrDecoder",
    "AddrInfo",
    "AddrMap",
    "AddrMapRef",
    "AddrMaster",
    "AddrMatrix",
    "AddrRange",
    "AddrRef",
    "AddrSlave",
    "AddrmapRef",
    "Addrspace",
    "AddrspaceAlias",
    "AddrspaceFilter",
    "Addrspaces",
    "DataInfo",
    "DataType",
    "DefaultAddrspace",
    "Defines",
    "Depth",
    "Field",
    "FieldFilter",
    "FillAddrspaceFactory",
    "FillFieldFactory",
    "FillWordFactory",
    "FullError",
    "GetAttrspacesFunc",
    "NamingScheme",
    "ReadOp",
    "ReservedAddrspace",
    "Size",
    "SlaveAddrspace",
    "ToAccess",
    "ToAddrMapRef",
    "Word",
    "WordFields",
    "WordFilter",
    "WordInfo",
    "Words",
    "WriteOp",
    "any_read",
    "calc_depth_size",
    "cast_access",
    "check_data",
    "create_fill_addrspace",
    "create_fill_field",
    "create_fill_word",
    "get_addrmap",
    "get_addrspaces",
    "get_counteraccess",
    "get_datatype",
    "get_is_const",
    "get_is_volatile",
    "get_mask",
    "get_size",
    "is_read_repeatable",
    "is_write_repeatable",
    "join_addrspaces",
    "name_alpha",
    "read_on_modify",
    "resolve",
    "resolve_field_value",
    "resolves",
    "split_keyvaluepairs",
    "zip_addrspaces",
]
