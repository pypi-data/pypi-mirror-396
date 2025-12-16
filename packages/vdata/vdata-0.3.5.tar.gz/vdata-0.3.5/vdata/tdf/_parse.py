from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from typing import Any
from warnings import warn

import ezarr as ez
import numpy as np
import numpy.typing as npt
import numpy_indexed as npi
import pandas as pd
from zarr.core.attributes import Attributes

import vdata.timepoint as tp
from vdata._typing import IFS, NDArrayLike_IFS, NDArrayList_IFS, np_IFS
from vdata.array_view import NDArrayView
from vdata.names import NO_NAME
from vdata.tdf.index import RepeatingIndex
from vdata.utils import obj_as_str


class TimedArray:
    __slots__: tuple[str, ...] = "arr", "time"

    def __init__(self, arr: RepeatingIndex | None, time: tp.TimePointIndex | None):
        if arr is None and isinstance(time, tp.TimePointIndex):
            self.arr: RepeatingIndex = RepeatingIndex(np.arange(len(time)))
            self.time: tp.TimePointIndex = time

        elif arr is not None and time is None:
            self.arr = arr
            self.time = tp.TimePointIndex(tp.TimePointNArray([0], unit="h"), ranges=np.array([len(arr)]))

        elif isinstance(arr, RepeatingIndex) and isinstance(time, tp.TimePointIndex):
            if len(arr) != len(time):
                raise ValueError(f"Length of 'time_list' ({len(time)}) did not match length of 'index' ({len(arr)}).")

            self.arr = arr
            self.time = time

        elif arr is None and time is None:
            self.arr = RepeatingIndex(np.empty(0, dtype=np.float64))
            self.time = tp.TimePointIndex(tp.TimePointNArray([]), ranges=np.array([]))

        else:
            raise NotImplementedError


def _sort_and_get_tp(
    data: pd.DataFrame | None,
    col_name: str | None,
    timepoints: tp.TimePointNArray | NDArrayView[tp.TimePoint],
    sort: bool,
) -> tuple[tp.TimePointIndex, pd.DataFrame | None]:
    if sort:
        sorting_indices = np.argsort(timepoints, kind="stable").astype(int)
        tp_index = tp.TimePointIndex.from_array(timepoints[sorting_indices])  # pyright: ignore[reportArgumentType]

    else:
        # even though we do not wish to sort, timepoints must be reordered to group equal values together
        # but the appearance order will be preserved
        u, i, c = np.unique(timepoints, equal_nan=False, return_index=True, return_counts=True)
        tp_sorting_indices = sorted(i.astype(int))

        sorted_timepoints: tp.TimePointNArray = timepoints[tp_sorting_indices]
        sorted_ranges = np.cumsum(c[npi.indices(u, sorted_timepoints)])

        tp_index = tp.TimePointIndex(sorted_timepoints, sorted_ranges)

        sorting_indices = np.where(timepoints == sorted_timepoints[:, None])[1]

    if data is None:
        return tp_index, None

    if col_name is not None:
        del data[col_name]

    return tp_index, data.iloc[sorting_indices]


def _get_timed_index(
    index: RepeatingIndex | None,
    time_list: tp.TimePointNArray | NDArrayView[tp.TimePoint] | None,
    timepoints_column_name: str | None,
    data: pd.DataFrame | None,
    sort: bool,
) -> tuple[TimedArray, pd.DataFrame | None]:
    if isinstance(data, pd.DataFrame) and index is not None:
        data.index = pd.Index(index.values)

    if time_list is None and timepoints_column_name is not None:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("'timepoints_column_name' parameter was given without data.")

        if timepoints_column_name not in data.columns:
            raise ValueError(f"'timepoints_column_name' ('{timepoints_column_name}') is not in the data's columns.")

        _time_list, data = _sort_and_get_tp(
            data, timepoints_column_name, tp.as_timepointarray(data[timepoints_column_name]), sort=sort
        )

    elif time_list is not None:
        if timepoints_column_name is not None:
            warn("'time_list' parameter already supplied, 'timepoints_column_name' parameter is ignored.")

        _time_list, data = _sort_and_get_tp(data, timepoints_column_name, time_list, sort=sort)

    else:
        _time_list = None

    if isinstance(data, pd.DataFrame):
        unique_index = np.unique(data.index)

        if len(unique_index) == len(data.index):
            index = RepeatingIndex(data.index.values)

        else:
            n_repeats, mod = divmod(len(data.index), len(unique_index))

            if mod:
                raise ValueError("Index must be unique or repeating exactly.")

            index = RepeatingIndex(unique_index, repeats=n_repeats)

    return TimedArray(index, _time_list), data


def parse_data_h5(data: ez.EZDict[Any], lock: tuple[bool, bool] | None, name: str) -> Attributes:
    if lock is not None:
        data.attrs["locked_indices"], data.attrs["locked_columns"] = bool(lock[0]), bool(lock[1])

    if name != NO_NAME:
        data.attrs["name"] = str(name)

    return data.attrs


@dataclass
class ParsedData:
    numerical_array: npt.NDArray[np.int_ | np.float64]
    string_array: npt.NDArray[np.str_]
    timepoints_array: tp.TimePointIndex
    index: npt.NDArray[np_IFS]
    columns_numerical: npt.NDArray[np_IFS]
    columns_string: npt.NDArray[np_IFS]
    lock: tuple[bool, bool]
    timepoints_column_name: str | None
    name: str
    repeating_index: bool


def parse_data(
    data: Mapping[str, NDArrayList_IFS] | pd.DataFrame | NDArrayLike_IFS | None,
    index: Collection[IFS] | RepeatingIndex | None,
    columns: Collection[IFS] | None,
    timepoints: Collection[IFS | tp.TimePoint] | IFS | tp.TimePoint | None,
    timepoints_column_name: str | None,
    lock: tuple[bool, bool] | None,
    name: str,
    sort_timepoints: bool,
) -> ParsedData:
    """
    Parse the user-given data to create a TemporalDataFrame.

    Args:
        data: Optional object containing the data to store in this TemporalDataFrame. It can be :
            - a dictionary of ['column_name': [values]], where [values] has always the same length
            - a pandas DataFrame
            - a single value to fill the data with
        index: Optional indices to set or to substitute to indices defined in data if data is a pandas DataFrame.
        repeating_index: Is the index repeated at all time-points ?
            If False, the index must contain unique values.
            If True, the index must be exactly equal at all time-points.
        columns: Optional column names.
        timepoints: Optional list of time values of the same length as the index, indicating for each row at which
            time point it exists.
        timepoints_column_name: Optional column name in data (if data is a dict or a pandas DataFrame) to use as time data.
        lock: Optional 2-tuple of booleans indicating which axes (index, columns) are locked.
        name: A name for the TemporalDataFrame.
        sort_timepoints: Sort time-points in ascending order ?
    """
    if data is not None:
        data = pd.DataFrame(data).copy()

    if index is not None and not isinstance(index, RepeatingIndex):
        index = RepeatingIndex(index)

    timed_index, data = _get_timed_index(
        index,
        None if timepoints is None else tp.as_timepointarray(timepoints),
        timepoints_column_name,
        data,
        sort=sort_timepoints,
    )

    # TODO : test for when data is None but other parameters are given
    if data is None:
        if timepoints_column_name is not None:
            warn("No data supplied, 'timepoints_column_name' parameter is ignored.")

        return ParsedData(
            np.empty((len(timed_index.arr), 0 if columns is None else len(columns))),
            np.empty((len(timed_index.arr), 0), dtype=str),
            timed_index.time,
            timed_index.arr.values,
            np.empty(0) if columns is None else np.array(columns),
            np.empty(0),
            (False, False) if lock is None else (bool(lock[0]), bool(lock[1])),
            None,
            str(name),
            timed_index.arr.is_repeating,
        )

    numerical_array, string_array, columns_numerical, columns_string = parse_data_df(data, columns)

    return ParsedData(
        numerical_array,
        string_array,
        timed_index.time,
        obj_as_str(np.array(data.index)),
        columns_numerical,
        columns_string,
        (False, False) if lock is None else (bool(lock[0]), bool(lock[1])),
        timepoints_column_name,
        str(name),
        timed_index.arr.is_repeating,
    )


def parse_data_df(
    data: pd.DataFrame, columns: Collection[IFS] | None
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.str_], npt.NDArray[np_IFS], npt.NDArray[np_IFS]]:
    numerical_df = data.select_dtypes(include="number")
    string_df = data.select_dtypes(exclude="number")

    if columns is not None:
        columns_numerical = np.array(columns)[: numerical_df.shape[1]]
        columns_string = np.array(columns)[numerical_df.shape[1] :]

    else:
        columns_numerical = np.array(numerical_df.columns.values)
        columns_string = np.array(string_df.columns.values)

    # parse ARRAY NUM ---------------------------------------------------------
    # enforce 'float' data type
    numerical_array = numerical_df.values.astype(float)

    # parse ARRAY STR ---------------------------------------------------------
    # enforce 'string' data type
    string_array = string_df.values.astype(str)

    return numerical_array, string_array, obj_as_str(columns_numerical), obj_as_str(columns_string)
