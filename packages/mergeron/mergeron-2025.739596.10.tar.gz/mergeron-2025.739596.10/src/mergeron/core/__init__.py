"""Constants, types, objects and functions used within this sub-package."""

from __future__ import annotations

import shutil
from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any

import mpmath  # type: ignore
import numpy as np
from attrs import cmp_using, field, frozen
from numpy.random import PCG64DXSM

from .. import (  # noqa: TID252
    VERSION,
    ArrayBIGINT,
    ArrayDouble,
    this_yaml,
    yamelize_attrs,
    yaml_rt_mapper,
)
from .. import WORK_DIR as PKG_WORK_DIR  # noqa: TID252
from .. import data as mdat  # noqa: TID252

__version__ = VERSION

DEFAULT_BITGENERATOR = PCG64DXSM

type MPFloat = mpmath.ctx_mp_python.mpf
type MPMatrix = mpmath.matrices.matrices._matrix


@frozen
class GuidelinesBoundary:
    """Represents Guidelines boundary analytically."""

    coordinates: ArrayDouble
    """Market-share pairs as Cartesian coordinates of points on the boundary."""

    area: float
    """Area under the boundary."""


WORK_DIR = globals().get("WORK_DIR", PKG_WORK_DIR)
"""Redefined, in case the user defines WORK_DIR between module imports."""

FID_WORK_DIR = WORK_DIR / "FTCData"
if not FID_WORK_DIR.is_dir():
    FID_WORK_DIR.mkdir(parents=True)

INVDATA_ARCHIVE_PATH = WORK_DIR / mdat.FTC_MERGER_INVESTIGATIONS_DATA.name
if not INVDATA_ARCHIVE_PATH.is_file():
    shutil.copy2(mdat.FTC_MERGER_INVESTIGATIONS_DATA, INVDATA_ARCHIVE_PATH)  # type: ignore

TABLE_TYPES = ("ByHHIandDelta", "ByFirmCount")
CONC_TABLE_ALL = "Table 3.1"
CNT_TABLE_ALL = "Table 4.1"

TTL_KEY = 86825
CONC_HHI_DICT = {
    "0 - 1,799": 0,
    "1,800 - 1,999": 1800,
    "2,000 - 2,399": 2000,
    "2,400 - 2,999": 2400,
    "3,000 - 3,999": 3000,
    "4,000 - 4,999": 4000,
    "5,000 - 6,999": 5000,
    "7,000 - 10,000": 7000,
    "TOTAL": TTL_KEY,
}
CONC_DELTA_DICT = {
    "0 - 100": 0,
    "100 - 200": 100,
    "200 - 300": 200,
    "300 - 500": 300,
    "500 - 800": 500,
    "800 - 1,200": 800,
    "1,200 - 2,500": 1200,
    "2,500 - 5,000": 2500,
    "TOTAL": TTL_KEY,
}
CNT_FCOUNT_DICT = {
    "2 to 1": 2,
    "3 to 2": 3,
    "4 to 3": 4,
    "5 to 4": 5,
    "6 to 5": 6,
    "7 to 6": 7,
    "8 to 7": 8,
    "9 to 8": 9,
    "10 to 9": 10,
    "10 +": 11,
    "TOTAL": TTL_KEY,
}


def invert_map(_dict: Mapping[Any, Any]) -> Mapping[Any, Any]:
    """Invert mapping, mapping values to keys of the original mapping."""
    return {_v: _k for _k, _v in _dict.items()}


type INVData = MappingProxyType[
    str, MappingProxyType[str, MappingProxyType[str, INVTableData]]
]
type INVData_in = dict[str, dict[str, dict[str, INVTableData]]]


@frozen
class INVTableData:
    """Represents individual table of FTC merger investigations data."""

    industry_group: str
    additional_evidence: str
    data_array: ArrayBIGINT = field(eq=cmp_using(eq=np.array_equal))


yamelize_attrs(INVTableData)

(_, _) = (
    this_yaml.representer.add_representer(
        Decimal, lambda _r, _d: _r.represent_scalar("!Decimal", f"{_d}")
    ),
    this_yaml.constructor.add_constructor(
        "!Decimal", lambda _c, _n, /: Decimal(_c.construct_scalar(_n))
    ),
)


(_, _) = (
    this_yaml.representer.add_representer(
        mpmath.mpf, lambda _r, _d: _r.represent_scalar("!MPFloat", f"{_d}")
    ),
    this_yaml.constructor.add_constructor(
        "!MPFloat", lambda _c, _n, /: mpmath.mpf(_c.construct_scalar(_n))
    ),
)

(_, _) = (
    this_yaml.representer.add_representer(
        mpmath.matrix, lambda _r, _d: _r.represent_sequence("!MPMatrix", _d.tolist())
    ),
    this_yaml.constructor.add_constructor(
        "!MPMatrix",
        lambda _c, _n, /: mpmath.matrix(_c.construct_sequence(_n, deep=True)),
    ),
)

_, _ = (
    this_yaml.representer.add_representer(
        MappingProxyType,
        lambda _r, _d: _r.represent_mapping("!mappingproxy", dict(_d.items())),
    ),
    this_yaml.constructor.add_constructor(
        "!mappingproxy", lambda _c, _n: MappingProxyType(dict(**yaml_rt_mapper(_c, _n)))
    ),
)


def _dict_from_mapping(_p: Mapping[Any, Any], /) -> dict[Any, Any]:
    retval: dict[Any, Any] = {}
    for _k, _v in _p.items():
        retval |= {_k: _dict_from_mapping(_v)} if isinstance(_v, Mapping) else {_k: _v}
    return retval


def _mappingproxy_from_mapping(_p: Mapping[Any, Any], /) -> MappingProxyType[Any, Any]:
    retval: dict[Any, Any] = {}
    for _k, _v in _p.items():
        retval |= (
            {_k: _mappingproxy_from_mapping(_v)}
            if isinstance(_v, Mapping)
            else {_k: _v}
        )
    return MappingProxyType(retval)
