from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast, override

import ezarr as ez
import ezarr.inplace as ezi
import numpy as np
import numpy.typing as npt
import numpy_indexed as npi
import pandas as pd
import zarr
import zarr.api.asynchronous
from zarr.core.array import sync
from zarr.core.common import AccessModeLiteral

import vdata.timepoint as tp
from vdata._typing import (
    IFS,
    AnyNDArrayLike_IFS,
    AttrDict,
    Collection_IFS,
    NDArrayLike_IFS,
    NDArrayList_IFS,
    np_IFS,
)
from vdata.IO import VLockError
from vdata.names import DEFAULT_TIME_COL_NAME, NO_NAME
from vdata.tdf._parse import parse_data
from vdata.tdf.base import TemporalDataFrameBase
from vdata.tdf.index import RepeatingIndex
from vdata.utils import isCollection

if TYPE_CHECKING:
    from vdata.tdf.view import TemporalDataFrameView


class TemporalDataFrame(TemporalDataFrameBase):
    """
    An equivalent to pandas DataFrames that includes the notion of time on the rows.
    This class implements a modified sub-setting mechanism to subset on time points, rows and columns
    """

    def __init__(
        self,
        data: Mapping[str, NDArrayList_IFS] | pd.DataFrame | NDArrayLike_IFS | None = None,
        index: Collection_IFS | RepeatingIndex | None = None,
        columns: Collection[IFS] | None = None,
        timepoints: Collection[IFS | tp.TimePoint] | IFS | tp.TimePoint | None = None,
        timepoints_column_name: str | None = None,
        sort_timepoints: bool = True,
        lock: tuple[bool, bool] | None = None,
        name: str = NO_NAME,
    ):
        """
        Args:
            data: Optional object containing the data to store in this TemporalDataFrame. It can be :
                - a dictionary of ['column_name': [values]], where [values] has always the same length
                - a pandas DataFrame
                - a single value to fill the data with
            index: Optional collection of indices. Must match the total number of rows in this TemporalDataFrame,
                over all time-points.
            columns: Optional column names.
            timepoints: Optional list of time values of the same length as the index, indicating for each row at which
                time point it exists.
            timepoints_column_name: Optional column name in data (if data is a dictionary or a pandas DataFrame) to use as
                time list. This parameter will be ignored if the 'time_list' parameter was set.
            sort_timepoints: Sort time-points in ascending order ? (default: True).
            lock: Optional 2-tuple of booleans indicating which axes (index, columns) are locked.
                If 'index' is locked, .index.setter() and .reindex() cannot be used.
                If 'columns' is locked, .__delattr__(), .columns.setter() and .insert() cannot be used.
            name: a name for this TemporalDataFrame.
        """
        parsed_data = parse_data(
            data, index, columns, timepoints, timepoints_column_name, lock, name, sort_timepoints=sort_timepoints
        )

        super().__init__(
            index=parsed_data.index,
            timepoints_index=parsed_data.timepoints_array,
            array_numerical=parsed_data.numerical_array,
            array_string=parsed_data.string_array,
            columns_numerical=parsed_data.columns_numerical,
            columns_string=parsed_data.columns_string,
            attr_dict=AttrDict(
                name=parsed_data.name,
                timepoints_column_name=parsed_data.timepoints_column_name,
                locked_indices=parsed_data.lock[0],
                locked_columns=parsed_data.lock[1],
                repeating_index=parsed_data.repeating_index,
            ),
        )

    @override
    def __delattr__(self, column_name: str) -> None:
        """Drop a column."""
        if self.has_locked_columns:
            raise VLockError("Cannot delete column from tdf with locked columns.")

        if column_name in self._columns_numerical:
            item_index = np.where(self._columns_numerical == np.array(column_name))[0][0]
            self._array_numerical = ezi.delete(self._array_numerical, item_index, axis=1)
            self._columns_numerical = ezi.delete(self._columns_numerical, item_index)

        elif column_name in self.columns_str:
            item_index = np.where(self._columns_string == np.array(column_name))[0][0]
            self._array_string = ezi.delete(self._array_string, item_index, axis=1)
            self._columns_string = ezi.delete(self._columns_string, item_index)

        else:
            raise AttributeError(f"'{column_name}' not found in this TemporalDataFrame.")

    @override
    def __invert__(self) -> TemporalDataFrameView:
        """
        Invert the getitem selection behavior : all elements NOT present in the slicers will be selected.
        """
        raise NotImplementedError
        # return tdf.TemporalDataFrameView(
        #     parent=self,
        #     index_positions=np.arange(self.n_index),
        #     columns_numerical=self._columns_numerical,
        #     columns_string=self._columns_string,
        #     inverted=True,
        # )

    @override
    @classmethod
    def __ez_read__(cls, grp: ez.EZDict[Any]) -> TemporalDataFrame:
        obj = cls.__new__(cls)

        super().__init__(
            obj,
            index=grp["index"],
            timepoints_index=grp["timepoints_index"],
            array_numerical=grp["array_numerical"],
            array_string=grp["array_string"],
            columns_numerical=grp["columns_numerical"],
            columns_string=grp["columns_string"],
            attr_dict=grp.attrs,
            data=grp,
        )
        return obj

    @classmethod
    def read(
        cls,
        path: str | Path | zarr.Group | ez.EZDict[Any],
        mode: AccessModeLiteral = "r+",
    ) -> TemporalDataFrame:
        """
        Read a saved TemporalDataFrame from a local file.

        Args:
            path: path to a zarr local store.
            mode: mode for opening the zarr store. (default: "r+")
        """
        match path:
            case zarr.Group():
                dct = ez.EZDict[Any](path)

            case ez.EZDict():
                dct = path

            case _:
                dct = ez.EZDict[Any](zarr.open_group(path, mode=mode))

        return TemporalDataFrame.__ez_read__(dct)

    @classmethod
    def read_from_csv(
        cls,
        file: Path,
        sep: str = ",",
        timepoints: Collection[IFS | tp.TimePoint] | IFS | tp.TimePoint | None = None,
        timepoints_column_name: str | None = None,
        columns_dtype: str | None = None,
    ) -> TemporalDataFrame:
        """
        Read a .csv file into a TemporalDataFrame.

        Args:
            file: a path to the .csv file to read.
            sep: delimiter to use for reading the .csv file.
            timepoints: time points for the dataframe's rows. (see TemporalDataFrame's documentation for more details.)
            timepoints_column_name: if time points are not given explicitly with the 'time_list' parameter, a column name can be
                given. This column will be used as the time data.

        Returns:
            A TemporalDataFrame built from the .csv file.
        """
        df = pd.read_csv(file, index_col=0, sep=sep)

        timepoints_column_name = DEFAULT_TIME_COL_NAME if timepoints_column_name is None else timepoints_column_name

        if timepoints is None and timepoints_column_name == DEFAULT_TIME_COL_NAME:
            timepoints = df[timepoints_column_name].values.tolist()
            del df[timepoints_column_name]
            timepoints_column_name = None

        if columns_dtype is not None:
            df.columns = df.columns.astype(np.dtype(columns_dtype))

        return TemporalDataFrame(df, timepoints=timepoints, timepoints_column_name=timepoints_column_name)

    @property
    @override
    def name(self) -> str:
        """
        Get the name.
        """
        return super().name

    @name.setter
    def name(self, name: str) -> None:
        """Set the name."""
        self._attr_dict["name"] = str(name)

    @property
    @override
    def full_name(self) -> str:
        """
        Get the full name.
        """
        parts = []
        if self.empty:
            parts.append("empty")

        if self.is_backed:
            parts.append("backed")

        if len(parts):
            parts[0] = parts[0].capitalize()

        parts.append("TemporalDataFrame")
        if self.name != NO_NAME:
            parts.append(self.name)

        return " ".join(parts)

    @property
    @override
    def columns(self) -> npt.NDArray[np_IFS]:
        """
        Get the list of all column names.
        """
        return super().columns

    @columns.setter
    def columns(self, values: NDArrayLike_IFS) -> None:
        """
        Set the list of all column names.
        """
        if self.has_locked_columns:
            raise VLockError("Cannot set columns in tdf with locked columns.")

        if not (vs := len(values)) == (s := self.n_columns_num + self.n_columns_str):
            raise ValueError(f"Shape mismatch, new 'columns_num' values have shape {vs}, expected {s}.")

        self.columns_num[:] = values[: self.n_columns_num]
        self.columns_str[:] = values[self.n_columns_num :]

    @property
    @override
    def is_view(self) -> Literal[False]:
        """
        Is this a view on a TemporalDataFrame ?
        """
        return False

    @property
    @override
    def is_inverted(self) -> Literal[False]:
        """Is this an inverted view on a TemporalDataFrame ?"""
        return False

    @override
    def _append_column(self, column_name: IFS, values: npt.NDArray[np_IFS]) -> None:
        if np.issubdtype(values.dtype, np.number):
            self._array_numerical = np.insert(self._array_numerical, self.n_columns_num, values, axis=1)
            self._columns_numerical = np.insert(self._columns_numerical, self.n_columns_num, column_name)

        else:
            self._array_string = np.insert(self._array_string, self.n_columns_str, values, axis=1)
            self._columns_string = np.insert(self._columns_string, self.n_columns_str, column_name)

    @override
    def lock_indices(self) -> None:
        """Lock the "index" axis to prevent modifications."""
        self._attr_dict["locked_indices"] = True

    @override
    def unlock_indices(self) -> None:
        """Unlock the "index" axis to allow modifications."""
        self._attr_dict["locked_indices"] = False

    @override
    def lock_columns(self) -> None:
        """Lock the "columns" axis to prevent modifications."""
        self._attr_dict["locked_columns"] = True

    @override
    def unlock_columns(self) -> None:
        """Unlock the "columns" axis to allow modifications."""
        self._attr_dict["locked_columns"] = False

    @override
    def set_index(
        self,
        values: Collection[IFS] | RepeatingIndex,
        *,
        force: bool = False,
    ) -> None:
        """Set new index values."""
        if self.has_locked_indices and not force:
            raise VLockError("Cannot set index in TemporalDataFrame with locked index.")

        index = values if isinstance(values, RepeatingIndex) else RepeatingIndex(values)

        if not index.values.shape == self._index.shape:
            raise ValueError(
                f"Shape mismatch, new 'index' values have shape {index.values.shape}, expected {self._index.shape}."
            )

        self._index = _get_index_with_type(self._index, index.values.dtype)
        self._index[:] = index.values

        self._attr_dict["repeating_index"] = index.is_repeating

    def _get_index_positions(self, index: RepeatingIndex) -> npt.NDArray[np_IFS]:
        if not self._attr_dict["repeating_index"]:
            return cast(npt.NDArray[np.int_], npi.indices(self.index, index.values))

        if index.is_repeating:
            index_offset = 0
            index_0 = self.index_at(self.tp0)
            index_positions = np.zeros(len(index.values), dtype=int)
            first_positions = npi.indices(index_0, index.values[: len(index_0)])

            for tpi in range(self.n_timepoints):
                index_positions[tpi * len(index_0) : (tpi + 1) * len(index_0)] = first_positions + index_offset
                index_offset += len(index_0)

            return index_positions

        index_len_count = 0
        total_index = np.zeros((self.n_timepoints, len(index.values)), dtype=int)

        for tpi, timepoint in enumerate(self.timepoints):
            i_at_tp = self.index_at(timepoint)
            total_index[tpi] = npi.indices(i_at_tp, index.values) + index_len_count
            index_len_count += len(i_at_tp)

        return total_index.flatten()

    @override
    def reindex(self, order: npt.NDArray[np_IFS] | RepeatingIndex) -> None:
        """Re-order rows in this TemporalDataFrame so that their index matches the new given order."""
        index = order if isinstance(order, RepeatingIndex) else RepeatingIndex(order)

        # check all values in index
        if not np.all(np.isin(index.values, self.index)):
            raise ValueError("New index contains values which are not in the current index.")

        if index.is_repeating and not self._attr_dict["repeating_index"]:
            raise ValueError("Cannot set repeating index on tdf with non-repeating index.")

        elif not index.is_repeating and self._attr_dict["repeating_index"]:
            raise ValueError("Cannot set non-repeating index on tdf with repeating index.")

        # re-arrange rows to conform to new index
        index_positions = self._get_index_positions(index)

        self.set_index(index)
        self.values_num[:] = self.values_num[index_positions]
        self.values_str[:] = self.values_str[index_positions]

    def _check_before_insert(self, name: IFS, values: npt.NDArray[np_IFS] | Iterable[IFS] | IFS) -> npt.NDArray[np_IFS]:
        if self.has_locked_columns:
            raise VLockError("Cannot insert columns in tdf with locked columns.")

        if not isCollection(values):
            values = np.repeat(values, self.n_index)  # type: ignore[arg-type]

        values = np.array(values)

        if len(values) != self.n_index:
            raise ValueError(f"Wrong number of values ({len(values)}), expected {self.n_index}.")

        if name in self.columns:
            raise ValueError(f"A column named '{name}' already exists.")

        return values

    def insert(self, name: IFS, values: npt.NDArray[np_IFS] | Iterable[IFS] | IFS, *, loc: int = -1) -> None:
        """
        Insert a column in either the numerical data or the string data, depending on the type of the <values> array.
            The column is inserted at position <loc> with name <name>.
        """
        values = self._check_before_insert(name, values)

        if np.issubdtype(values.dtype, (np.int_, np.float64)):
            # create numerical column
            if loc < 0:
                loc += self.n_columns_num + 1

            self._array_numerical = np.insert(self._array_numerical, loc, values, axis=1)
            self._columns_numerical = np.insert(self._columns_numerical, loc, name)

        else:
            # create string column
            if loc < 0:
                loc += self.n_columns_str + 1

            self._array_string = np.insert(self._array_string, loc, values, axis=1)
            self._columns_string = np.insert(self._columns_string, loc, name)

    @override
    def merge(self, other: TemporalDataFrameBase, name: str | None = None) -> TemporalDataFrame:
        """
        Merge two TemporalDataFrames together, by rows. The column names and time points must match.

        Args:
            other: a TemporalDataFrame to merge with this one.
            name: a name for the merged TemporalDataFrame.

        Returns:
            A new merged TemporalDataFrame.
        """
        if not np.all(self.timepoints == other.timepoints):
            raise ValueError("Cannot merge TemporalDataFrames with different time points.")

        if not np.all(self.columns_num == other.columns_num) and not np.all(self.columns_str == other.columns_str):
            raise ValueError("Cannot merge TemporalDataFrames with different columns.")

        if not self.timepoints_column_name == other.timepoints_column_name:
            raise ValueError("Cannot merge TemporalDataFrames with different 'timepoints_column_name'.")

        if self._attr_dict["repeating_index"] is not other._attr_dict["repeating_index"]:
            raise ValueError("Cannot merge TemporalDataFrames if one has repeating index while the other has not.")

        if self.empty:
            combined_index = np.array([])
            for timepoint in self.timepoints:
                combined_index = np.concatenate(
                    (
                        combined_index,
                        self.index_at(timepoint),
                        other.index_at(timepoint),
                    )
                )

            _data = pd.DataFrame(index=combined_index, columns=self.columns)

        else:
            _assert_can_merge(self, other, self.tp0)
            _data = pd.concat(
                (self[self.tp0].to_pandas(), other[self.tp0].to_pandas()),  # type: ignore[union-attr]
            )

            for time_point in self.timepoints[1:]:
                _assert_can_merge(self, other, time_point)
                _data = pd.concat(
                    (
                        _data,
                        self[time_point].to_pandas(),  # type: ignore[union-attr]
                        other[time_point].to_pandas(),  # type: ignore[union-attr]
                    )
                )

            _data.columns = _data.columns.astype(self.columns.dtype)

        if self.timepoints_column_name is None:
            _time_list = [
                time_point
                for time_point in self.timepoints
                for _ in range(self.timepoints_index.n_at(time_point) + other.timepoints_index.n_at(time_point))
            ]

        else:
            _time_list = None

        return TemporalDataFrame(
            data=_data,
            columns=self.columns,
            timepoints=_time_list,
            timepoints_column_name=self.timepoints_column_name,
            name=name or f"{self.name} + {other.name}",
        )


def _get_index_with_type(
    index: AnyNDArrayLike_IFS, dtype: np.dtype[np.integer | np.floating | np.str_]
) -> NDArrayLike_IFS:
    if isinstance(index, zarr.Array):
        return zarr.Array(
            sync(
                zarr.api.asynchronous.from_array(index.store, name=index.path, data=index.astype(dtype), overwrite=True)  # pyright: ignore[reportAttributeAccessIssue]
            )
        )

    return np.empty(index.shape, dtype=dtype)


def _assert_can_merge(
    tdf1: TemporalDataFrameBase,
    tdf2: TemporalDataFrameBase,
    timepoint: tp.TimePoint,
) -> None:
    if np.any(np.isin(tdf1.index_at(timepoint), tdf2.index_at(timepoint))):
        raise ValueError(f"TemporalDataFrames to merge have index values in common at time point '{timepoint}'.")
