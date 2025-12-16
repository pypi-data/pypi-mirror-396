from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from ezarr.dataframe import EZDataFrame
import zarr

from vdata.data._parse.time import check_time_match
from vdata.data._parse.utils import log_timepoints
from vdata.IO.logger import generalLogger
from vdata.names import NO_NAME
from vdata.tdf import RepeatingIndex, TemporalDataFrame, TemporalDataFrameBase, TemporalDataFrameView
from vdata.timepoint import TimePointNArray
from vdata.utils import first_in

if TYPE_CHECKING:
    from vdata.data._parse.data import ParsingDataIn


def _index(obj: pd.DataFrame | EZDataFrame | TemporalDataFrameBase) -> RepeatingIndex:
    if isinstance(obj, TemporalDataFrameBase) and obj.index.is_repeating:
        return RepeatingIndex(obj.index_at(obj.tp0), repeats=obj.n_timepoints)

    return RepeatingIndex(obj.index)


def get_obs_index(
    data: pd.DataFrame
    | EZDataFrame
    | TemporalDataFrameBase
    | Mapping[str, pd.DataFrame | EZDataFrame | TemporalDataFrameBase]
    | None,
    obs: pd.DataFrame | EZDataFrame | TemporalDataFrameBase | None,
) -> RepeatingIndex | None:
    if obs is not None:
        return _index(obs)

    if isinstance(data, (pd.DataFrame, EZDataFrame, TemporalDataFrameBase)):
        return _index(data)

    if isinstance(data, dict):
        return _index(first_in(data))

    return None


def parse_obs(data: ParsingDataIn) -> TemporalDataFrameBase:
    # find time points list
    check_time_match(data)
    log_timepoints(data.timepoints)

    if isinstance(data.obs, (pd.DataFrame, EZDataFrame)):
        return TemporalDataFrame(data.obs)

    return data.obs


def parse_obsm(data: ParsingDataIn) -> dict[str, TemporalDataFrame | TemporalDataFrameView]:
    if not len(data.obsm):
        generalLogger.debug("    3. \u2717 'obsm' was not given.")
        return {}

    generalLogger.debug(f"    3. \u2713 'obsm' is a {type(data.obsm).__name__}.")

    if not isinstance(data.obsm, dict):
        raise TypeError("'obsm' must be a dictionary of DataFrames.")

    valid_obsm: dict[str, TemporalDataFrame | TemporalDataFrameView] = {}

    for key, value in data.obsm.items():
        if isinstance(value, (pd.DataFrame, EZDataFrame)):
            if data.timepoints_list is None:
                data.timepoints_list = TimePointNArray(data.obs.timepoints_column)

            valid_obsm[str(key)] = TemporalDataFrame(value, timepoints=data.timepoints_list, name=str(key))

        elif isinstance(value, TemporalDataFrame):
            value.unlock_indices()
            value.unlock_columns()

            if value.name != str(key):
                value.name = str(key) if value.name == NO_NAME else f"{value.name}_{key}"

            valid_obsm[str(key)] = value

        else:
            raise TypeError(f"'obsm' '{key}' must be a TemporalDataFrame or a pandas DataFrame.")

        if not np.all(np.isin(valid_obsm[str(key)].index, data.obs.index)):
            raise ValueError(f"Index of 'obsm' '{key}' does not match 'obs' and 'layers' indexes.")

        valid_obsm[str(key)].reindex(np.array(data.obs.index))

    return valid_obsm


def parse_obsp(data: ParsingDataIn) -> dict[str, EZDataFrame]:
    if not len(data.obsp):
        generalLogger.debug("    4. \u2717 'obsp' was not given.")
        return {}

    generalLogger.debug(f"    4. \u2713 'obsp' is a {type(data.obsp).__name__}.")

    if not len(data.layers):
        raise ValueError("'obsp' parameter cannot be set unless either 'data' or 'obs' are set.")

    if not isinstance(data.obsp, dict):
        raise TypeError("'obsp' must be a dictionary of 2D numpy arrays or pandas DataFrames.")

    valid_obsp: dict[str, EZDataFrame] = {}

    for key, value in data.obsp.items():
        if not isinstance(value, (np.ndarray, pd.DataFrame, EZDataFrame)) or value.ndim != 2:  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"'obsp' '{key}' must be a 2D numpy array or pandas DataFrame.")

        if isinstance(value, (pd.DataFrame, EZDataFrame)):
            if not all(value.index.isin(data.obs.index)):
                raise ValueError(f"Index of 'obsp' '{key}' does not match 'obs' and 'layers' indexes.")

            if not all(value.columns.isin(data.obs.index)):
                raise ValueError("Column names of 'obsp' do not match 'obs' and 'layers' indexes.")

            value.reindex(np.array(data.obs.index))
            value = EZDataFrame(value[np.array(data.obs.index)])

        else:
            value = EZDataFrame(value, index=data.obs.index, columns=data.obs.index)

        valid_obsp[str(key)] = value

    return valid_obsp
