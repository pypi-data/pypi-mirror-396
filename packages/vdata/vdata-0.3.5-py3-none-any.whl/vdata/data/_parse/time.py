from __future__ import annotations

from collections.abc import Collection
from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd
from anndata._core.xarray import Dataset2D
from ezarr.dataframe import EZDataFrame

import vdata.timepoint as tp
from vdata.array_view import NDArrayView
from vdata.data._parse.utils import log_timepoints
from vdata.IO.logger import generalLogger
from vdata.tdf import TemporalDataFrameBase, TemporalDataFrameView
from vdata.utils import first_in

if TYPE_CHECKING:
    from vdata.data._parse.data import ParsingDataIn


def parse_timepoints_list(
    timepoints_list: Collection[str | tp.TimePoint] | tp.TimePointNArray | None,
    timepoints_column_name: str | None,
    obs: pd.DataFrame | EZDataFrame | Dataset2D | TemporalDataFrameBase | None,
) -> tp.TimePointNArray | NDArrayView[tp.TimePoint] | None:
    if timepoints_list is not None:
        return tp.as_timepointarray(timepoints_list)

    elif obs is not None and timepoints_column_name is not None:
        if timepoints_column_name not in obs.columns:
            raise ValueError(f"Could not find column '{timepoints_column_name}' in obs.")

        if isinstance(obs, TemporalDataFrameBase):
            column = cast(TemporalDataFrameView, obs[timepoints_column_name])
            return tp.as_timepointarray(column.values)

        return tp.as_timepointarray(obs[timepoints_column_name])

    return None

    # TODO : could also get timepoints_list from obsm and obsp


def parse_timepoints(timepoints: pd.DataFrame | EZDataFrame | tp.TimePointLike | None) -> EZDataFrame:
    if timepoints is None:
        generalLogger.debug("  'time points' DataFrame was not given.")
        return EZDataFrame(pd.DataFrame(columns=np.array(["value", "unit"])), dtypes={"value": float, "unit": str})

    if not isinstance(timepoints, (pd.DataFrame, EZDataFrame)):
        try:
            timepoint = tp.TimePoint(timepoints)

        except ValueError:
            raise TypeError(f"'time points' must be a DataFrame or TimePointLike, got '{timepoints}'.")

        else:
            return EZDataFrame({"value": [timepoint.value], "unit": [timepoint.unit]})

    if "value" not in timepoints.columns:
        raise ValueError("'time points' must have at least a column 'value' to store time points value.")

    to_drop = ["value"]

    if "unit" in timepoints.columns:
        timepoints_col = tp.as_timepointarray(
            [f"{value}{unit}" for value, unit in zip(timepoints.value, timepoints.unit)]
        )
        to_drop.append("unit")

    else:
        timepoints_col = tp.as_timepointarray(timepoints["value"])

    timepoints_col.sort()

    timepoints = EZDataFrame(timepoints.drop(to_drop, axis=1))
    timepoints.insert(0, "value", np.array(timepoints_col))
    timepoints.insert(1, "unit", np.repeat(timepoints_col.unit, len(timepoints_col)))
    log_timepoints(timepoints)

    return timepoints


def check_time_match(data: ParsingDataIn) -> None:
    """
    Build timepoints DataFrame if it was not given by the user but 'timepoints_list' or 'timepoints_column_name' were given.
    Otherwise, if both timepoints and 'timepoints_list' or 'timepoints_column_name' were given, check that they match.
    """
    if data.timepoints.empty and data.timepoints_list is None and data.timepoints_column_name is None:
        # timepoints cannot be guessed
        return

    # build timepoints DataFrame from timepoints_list or timepoints_column_name
    if data.timepoints.empty and data.timepoints_list is not None:
        timepoints = np.unique(data.timepoints_list, equal_nan=False)

        data.timepoints["value"] = np.array(timepoints)
        data.timepoints["unit"] = np.repeat(timepoints.unit, len(timepoints))

        return

    if data.timepoints.empty and len(data.layers):
        timepoints = np.unique(first_in(data.layers).timepoints, equal_nan=False)

        data.timepoints["value"] = np.array(timepoints)
        data.timepoints["unit"] = np.repeat(timepoints.unit, len(timepoints))

        return

    # check that timepoints and _time_list and _timepoints_column_name match
    if data.timepoints_list is not None and not np.all(
        np.isin(data.timepoints_list, tp.as_timepointarray(data.timepoints.value))
    ):
        raise ValueError("There are values in 'timepoints_list' unknown in 'timepoints'.")

    elif data.timepoints_column_name is not None and not np.all(
        np.isin(tp.as_timepointarray(data.obs["timepoints"]), tp.as_timepointarray(data.timepoints.value))
    ):
        raise ValueError(f"There are values in obs['{data.timepoints_column_name}'] unknown in 'timepoints'.")
