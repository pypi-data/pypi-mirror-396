"""Methods to format and print summary statistics on merger enforcement patterns."""

import enum
from collections.abc import Mapping

import numpy as np
from scipy.interpolate import make_interp_spline  # type: ignore

from .. import VERSION, ArrayBIGINT, Enameled, this_yaml  # noqa: TID252
from ..core import TABLE_TYPES, INVData, INVTableData  # noqa: TID252
from . import INVResolution

__version__ = VERSION


@this_yaml.register_class
@enum.unique
class IndustryGroup(str, Enameled):
    """Industry group of reported markets."""

    ALL = "All Markets"
    GRO = "Grocery Markets"
    OIL = "Oil Markets"
    CHM = "Chemical Markets"
    PHM = "Pharmaceuticals Markets"
    HOS = "Hospital Markets"
    EDS = "Electronically-Controlled Devices and Systems Markets"
    BRD = "Branded Consumer Goods Markets"
    OTH = '"Other" Markets'
    IIC = "Industries in Common"


@this_yaml.register_class
@enum.unique
class OtherEvidence(str, Enameled):
    """Additional evidence available, if any, for reported markets."""

    HOT = "Hot Documents Identified"
    NHT = "No Hot Documents Identified"
    HTU = "No Evidence on Hot Documents"
    NCC = "No Strong Customer Complaints"
    SCC = "Strong Customer Complaints"
    CCU = "No Evidence on Customer Complaints"
    END = "Entry Difficult"
    EEY = "Entry Easy"
    EEU = "No Entry Evidence"
    UNR = "Unrestricted on additional evidence"


@this_yaml.register_class
@enum.unique
class StatsGrpSelector(str, Enameled):
    """Measure used to summarize investigations data."""

    FC = "ByFirmCount"
    DL = "ByDelta"
    HD = "ByHHIandDelta"


@this_yaml.register_class
@enum.unique
class StatsReturnSelector(str, Enameled):
    """Statistics to report on investigations data."""

    CNT = "count"
    RPT = "rate, point"
    RIN = "rate, interval"


@this_yaml.register_class
@enum.unique
class SortSelector(str, Enameled):
    """Sort order for reporting investigations data."""

    UCH = "unchanged"
    REV = "reversed"


# Parameters and functions to interpolate selected HHI and ΔHHI values
#   recorded in fractions to ranges of values in points on the HHI scale
HHI_POST_KNOTS = np.array([0, 1800, 2000, 2400, 3000, 4000, 5000, 7000, 10001], int)
HHI_DELTA_KNOTS = np.array([0, 100, 200, 300, 500, 800, 1200, 2500, 5001], int)
hhi_post_ranger, hhi_delta_ranger = (
    make_interp_spline(_f / 1e4, _f, k=0) for _f in (HHI_POST_KNOTS, HHI_DELTA_KNOTS)
)


def enf_cnts_obs_by_group(
    _invdata_array_dict: INVData,
    _study_period: str,
    _table_ind_grp: IndustryGroup,
    _table_evid_cond: OtherEvidence,
    _stats_group: StatsGrpSelector,
    _enf_spec: INVResolution,
    /,
) -> ArrayBIGINT:
    """Summarize investigations data by reporting group.

    Parameters
    ----------
    _invdata_array_dict
        raw investigations data
    _study_period
        study period
    _table_ind_grp
        industry group
    _table_evid_cond
        additional evidence
    _stats_group
        grouping measure
    _enf_spec
        enforcement specification (see, :class:`mergeron.gen.INVResolution`)

    Returns
    -------
    ArrayBIGINT
        Counts of markets resolved as enforced, cleared, or both, respectively.
    """
    match _stats_group:
        case StatsGrpSelector.FC:
            cnts_func = enf_cnts_byfirmcount
            cnts_listing_func = enf_cnts_obs_byfirmcount
        case StatsGrpSelector.DL:
            cnts_func = enf_cnts_bydelta
            cnts_listing_func = enf_cnts_obs_byhhianddelta
        case StatsGrpSelector.HD:
            cnts_func = enf_cnts_byhhianddelta
            cnts_listing_func = enf_cnts_obs_byhhianddelta

    return cnts_func(
        cnts_listing_func(
            _invdata_array_dict,
            _study_period,
            _table_ind_grp,
            _table_evid_cond,
            _enf_spec,
        )
    )


def enf_cnts_obs_byfirmcount(
    _data_array_dict: INVData,
    _data_period: str = "1996-2003",
    _table_ind_group: IndustryGroup = IndustryGroup.ALL,
    _table_evid_cond: OtherEvidence = OtherEvidence.UNR,
    _enf_spec: INVResolution = INVResolution.ENFT,
    /,
) -> ArrayBIGINT:
    """Summarize investigations data by firm count.

    Parameters
    ----------
    _data_array_dict
        raw investigations data
    _data_period
        data period
    _table_ind_group
        industry group
    _table_evid_cond
        additional evidence
    _enf_spec
        enforcement specification (see, :class:`mergeron.gen.INVResolution`)

    Returns
    -------
    ArrayBIGINT
        Counts of markets resolved as enforced, cleared, or both, respectively,
        reported by number of pre-merger firms.
    """
    if _data_period not in _data_array_dict:
        raise ValueError(
            f"Invalid value of data period, {f'"{_data_period}"'}."
            f"Must be one of, {tuple(_data_array_dict.keys())!r}."
        )

    data_array_dict_sub = _data_array_dict[_data_period][TABLE_TYPES[1]]

    table_no_ = table_no_lku(data_array_dict_sub, _table_ind_group, _table_evid_cond)

    cnts_array = data_array_dict_sub[table_no_].data_array

    ndim_in = 1
    stats_kept_indxs = []
    match _enf_spec:
        case INVResolution.CLRN:
            stats_kept_indxs = [-1, -2]
        case INVResolution.ENFT:
            stats_kept_indxs = [-1, -3]
        case INVResolution.BOTH:
            stats_kept_indxs = [-1, -3, -2]

    return np.hstack([cnts_array[:, :ndim_in], cnts_array[:, stats_kept_indxs]])


def enf_cnts_obs_byhhianddelta(
    _data_array_dict: INVData,
    _data_period: str = "1996-2003",
    _table_ind_group: IndustryGroup = IndustryGroup.ALL,
    _table_evid_cond: OtherEvidence = OtherEvidence.UNR,
    _enf_spec: INVResolution = INVResolution.ENFT,
    /,
) -> ArrayBIGINT:
    """Summarize investigations data by HHI and ΔHHI.

    Parameters
    ----------
    _data_array_dict
        raw investigations data
    _data_period
        data period
    _table_ind_group
        industry group
    _table_evid_cond
        additional evidence
    _enf_spec
        enforcement specification (see, :class:`mergeron.gen.INVResolution`)

    Returns
    -------
    ArrayBIGINT
        Counts of markets resolved as enforced, cleared, or both, respectively,
        reported by HHI and ΔHHI.
    """
    if _data_period not in _data_array_dict:
        raise ValueError(
            f"Invalid value of data period, {f'"{_data_period}"'}."
            f"Must be one of, {tuple(_data_array_dict.keys())!r}."
        )

    data_array_dict_sub = _data_array_dict[_data_period][TABLE_TYPES[0]]

    table_no_ = table_no_lku(data_array_dict_sub, _table_ind_group, _table_evid_cond)

    cnts_array = data_array_dict_sub[table_no_].data_array

    ndim_in = 2
    stats_kept_indxs = []
    match _enf_spec:
        case INVResolution.CLRN:
            stats_kept_indxs = [-1, -2]
        case INVResolution.ENFT:
            stats_kept_indxs = [-1, -3]
        case INVResolution.BOTH:
            stats_kept_indxs = [-1, -3, -2]

    return np.hstack([cnts_array[:, :ndim_in], cnts_array[:, stats_kept_indxs]])


def table_no_lku(
    _data_array_dict_sub: Mapping[str, INVTableData],
    _table_ind_group: IndustryGroup = IndustryGroup.ALL,
    _table_evid_cond: OtherEvidence = OtherEvidence.UNR,
    /,
) -> str:
    """Lookup table number based on industry group and additional evidence."""
    if _table_evid_cond not in (
        _egl := [
            _data_array_dict_sub[_v].additional_evidence for _v in _data_array_dict_sub
        ]
    ):
        raise ValueError(
            f"Invalid value for additional evidence, {f'"{_table_evid_cond}"'}."
            f"Must be one of {_egl!r}"
        )
    if _table_ind_group not in (
        _igl := [_data_array_dict_sub[_v].industry_group for _v in _data_array_dict_sub]
    ):
        raise ValueError(
            f"Invalid value for industry group, {f'"{_table_ind_group}"'}."
            f"Must be one of {_igl!r}"
        )

    tno_ = next(
        _t
        for _t in _data_array_dict_sub
        if all((
            _data_array_dict_sub[_t].industry_group == _table_ind_group,
            _data_array_dict_sub[_t].additional_evidence == _table_evid_cond,
        ))
    )

    return tno_


def enf_cnts_byfirmcount(_raw_counts: ArrayBIGINT, /) -> ArrayBIGINT:
    """Summarize investigations data by firm count.

    Parameters
    ----------
    _raw_counts
        raw investigations data array

    Returns
    -------
    ArrayBIGINT
        Subtotals for columns other than the first, grouped by the first column.
    """
    if not _raw_counts[:, 0].any():
        return np.array([], int)

    ndim_in = 1
    return np.vstack([
        np.concatenate([
            (_i,),
            np.einsum(
                "ij->j", _raw_counts[_raw_counts[:, 0] == _i][:, ndim_in:], dtype=int
            ),
        ])
        for _i in np.unique(_raw_counts[:, 0])
    ])


def enf_cnts_bydelta(_raw_counts: ArrayBIGINT, /) -> ArrayBIGINT:
    """Summarize investigations data by ΔHHI.

    Parameters
    ----------
    _raw_counts
        raw investigations data array

    Returns
    -------
    ArrayBIGINT
        Subtotals for columns higher than the second, grouped by the second column.
    """
    if not _raw_counts[:, 1].any():
        return np.array([], int)
    ndim_in = 2
    return np.vstack([
        np.concatenate([
            (_k,),
            np.einsum(
                "ij->j", _raw_counts[_raw_counts[:, 1] == _k][:, ndim_in:], dtype=int
            ),
        ])
        for _k in HHI_DELTA_KNOTS[:-1]
    ])


def enf_cnts_byhhianddelta(_raw_counts: ArrayBIGINT, /) -> ArrayBIGINT:
    """Summarize investigations data by concentration zone, as defined in the Guidelines.

    Includes sub-total detail for "Moderately Concentrated" and "Unconcentrated" markets.

    Parameters
    ----------
    _raw_counts
        raw investigations data array

    Returns
    -------
    ArrayBIGINT
        Subtotals range of HHI and ΔHHI, with detail
    """
    if not _raw_counts[:, 0].any() or np.isnan(_raw_counts[:, 0]).all():
        return np.array([], int)
    _ndim_in = 2
    cnts_byhhipostanddelta: ArrayBIGINT = np.zeros((1, _raw_counts.shape[1]), dtype=int)

    # rollup clearance stats by HHI and Delta thresholds
    for _hhi_post_lim in HHI_POST_KNOTS[:-1]:
        hhi_test_array = _raw_counts[_raw_counts[:, 0] == _hhi_post_lim]

        for _delta_lim in HHI_DELTA_KNOTS[:-1]:
            delta_test_array = hhi_test_array[hhi_test_array[:, 1] == _delta_lim]

            cnts_byhhipostanddelta = np.vstack((
                cnts_byhhipostanddelta,
                np.asarray(
                    [
                        _hhi_post_lim,
                        _delta_lim,
                        *np.einsum("ij->j", delta_test_array[:, _ndim_in:], dtype=int),
                    ],
                    dtype=int,
                ),
            ))
    return cnts_byhhipostanddelta[1:]
