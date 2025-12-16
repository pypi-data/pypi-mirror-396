from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Collection, Generator, Iterable
from functools import partialmethod
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast, overload, override

import ezarr as ez
import numpy as np
import numpy.typing as npt
import pandas as pd
import zarr
from zarr.core.attributes import Attributes
from zarr.core.common import AccessModeLiteral
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]

import vdata.tdf as tdf
import vdata.timepoint as tp
from vdata._typing import (
    IF,
    IFS,
    AnyNDArrayLike,
    AnyNDArrayLike_IF,
    AnyNDArrayLike_IFS,
    AttrDict,
    MultiSlicer,
    Slicer,
    np_IFS,
)
from vdata.array_view import NDArrayView
from vdata.IO import VLockError
from vdata.names import DEFAULT_TIME_COL_NAME
from vdata.tdf._parse import parse_data_h5
from vdata.tdf.index import RepeatingIndex
from vdata.tdf.indexers import VAtIndexer, ViAtIndexer, ViLocIndexer, VLocIndexer
from vdata.tdf.indexing import as_slicer, parse_slicer, parse_values
from vdata.utils import are_equal, repr_array

if TYPE_CHECKING:
    from vdata.tdf.dataframe import TemporalDataFrame
    from vdata.tdf.view import TemporalDataFrameView


VERTICAL_SEPARATOR: str = "\uff5c"


def underlined(text: str) -> str:
    return text + "\n" + "\u203e" * len(text)


class TemporalDataFrameBase(ABC, ez.SupportsEZReadWrite):
    """
    Abstract base class for all TemporalDataFrames.
    """

    _attributes: set[str] = {
        "_attr_dict",
        "_index",
        "_timepoints_index",
        "_columns_numerical",
        "_columns_string",
        "_array_numerical",
        "_array_string",
        "_data",
        "_timepoint_masks",
    }

    def __init__(
        self,
        index: AnyNDArrayLike_IFS,
        timepoints_index: tp.TimePointIndex,
        array_numerical: AnyNDArrayLike_IF,
        array_string: AnyNDArrayLike[np.str_],
        columns_numerical: AnyNDArrayLike_IFS,
        columns_string: AnyNDArrayLike_IFS,
        attr_dict: AttrDict | Attributes,
        data: ez.EZDict[Any] | None = None,
    ):
        self._index: AnyNDArrayLike_IFS = index
        self._timepoints_index: tp.TimePointIndex = timepoints_index
        self._columns_numerical: AnyNDArrayLike_IFS = columns_numerical
        self._columns_string: AnyNDArrayLike_IFS = columns_string
        self._array_numerical: AnyNDArrayLike_IF = array_numerical
        self._array_string: AnyNDArrayLike[np.str_] = array_string

        self._attr_dict: AttrDict | Attributes = attr_dict
        self._data: ez.EZDict[Any] | None = data

    @override
    def __repr__(self) -> str:
        return f"{self.full_name}\n{self.head()}"

    @override
    def __dir__(self) -> Iterable[str]:
        return chain(super().__dir__(), map(str, self.columns))

    def __getattr__(self, column_name: str) -> TemporalDataFrameView:
        """
        Get a single column.
        """
        try:
            return cast("TemporalDataFrameView", self.__getitem__(np.s_[:, :, column_name]))
        except (KeyError, ValueError) as e:
            raise AttributeError from e

    @override
    def __setattr__(self, name: IFS, values: npt.NDArray[np_IFS]) -> None:
        """
        Set values of a single column. If the column does not already exist in this TemporalDataFrame, it is created
            at the end.
        """
        if isinstance(name, str) and (name in self._attributes or name in object.__dir__(self)):
            object.__setattr__(self, name, values)
            return

        try:
            values = np.broadcast_to(values, self.n_index)

        except ValueError:
            raise ValueError(f"Can't broadcast values to ({self.n_index},) for column '{name}'.")

        if name in self.columns_num:
            idx: np.integer = np.argwhere(self._columns_numerical == np.array(name))[0, 0]
            self._array_numerical[:, idx] = values
        elif name in self.columns_str:
            idx = np.argwhere(self._columns_string == np.array(name))[0, 0]
            self._array_string[:, idx] = values

        else:
            self._append_column(name, values)

    @override
    @abstractmethod
    def __delattr__(self, key: str) -> None:
        pass

    @overload
    def __getitem__(self, slicer: IFS | tp.TimePoint | range | slice) -> TemporalDataFrameBase: ...
    @overload
    def __getitem__(self, slicer: tuple[Slicer, Slicer]) -> TemporalDataFrameBase: ...
    @overload
    def __getitem__(self, slicer: tuple[IFS | tp.TimePoint, IFS, IFS]) -> IFS: ...
    @overload
    def __getitem__(self, slicer: tuple[MultiSlicer, Slicer, Slicer]) -> TemporalDataFrameBase: ...
    def __getitem__(
        self, slicer: Slicer | tuple[Slicer, Slicer] | tuple[Slicer, Slicer, Slicer]
    ) -> TemporalDataFrameBase | IFS:
        """
        Get a subset.
        """
        _numerical_selection, _string_selection = parse_slicer(self, as_slicer(slicer))

        if _numerical_selection.is_empty and _string_selection.is_empty:
            return self

        if _numerical_selection.contains_empty_list and np.prod(_string_selection.out_shape) == 1:
            return cast(IFS, self._array_string[_string_selection.get_indexers()][0, 0])

        if _string_selection.contains_empty_list and np.prod(_numerical_selection.out_shape) == 1:
            return cast(IFS, self._array_numerical[_numerical_selection.get_indexers()][0, 0])

        return tdf.TemporalDataFrameView(
            parent=self,
            numerical_selection=_numerical_selection,
            string_selection=_string_selection,
            inverted=self.is_inverted,
        )

    def __setitem__(
        self,
        slicer_: Slicer | tuple[Slicer, Slicer] | tuple[Slicer, Slicer, Slicer],
        values: IFS | Collection[IFS] | TemporalDataFrameBase,
    ) -> None:
        """
        Set values in a subset.
        """
        slicer = as_slicer(slicer_)

        if slicer.targets_single_column():
            return self.__setattr__(slicer.col, values)

        _numerical_selection, _string_selection = parse_slicer(self, slicer)
        _numerical_values, _string_values = parse_values(
            np.array(values), slicer.col, self, _numerical_selection, _string_selection
        )

        if _numerical_values is not None:
            self._array_numerical[_numerical_selection.get_indexers()] = _numerical_values

        if _string_values is not None:
            self._array_string[_string_selection.get_indexers()] = _string_values

    def __delitem__(self, key: str) -> None:
        self.__delattr__(key)

    def _check_compatibility(self, value: TemporalDataFrameBase) -> None:
        # time-points column and nb of columns must be identical
        if not np.array_equal(self.timepoints_column, value.timepoints_column):
            raise ValueError("Time-points do not match.")
        if not np.array_equal(self.n_columns_num, value.n_columns_num):
            raise ValueError("Columns numerical do not match.")
        if not np.array_equal(self.n_columns_str, value.n_columns_str):
            raise ValueError("Columns string do not match.")

    def _add_core(self, value: IFS | TemporalDataFrameBase) -> TemporalDataFrame:
        """
        Internal function for adding a value, called from __add__. Do not use directly.
        """
        if isinstance(value, (int, float, np.integer, np.floating)):
            if self._array_numerical.size == 0:
                raise ValueError("No numerical data to add to.")

            values_num = cast(AnyNDArrayLike_IF, self._array_numerical + value)
            values_str = self._array_string
            value_name: IFS = value

        elif isinstance(value, tdf.TemporalDataFrameBase):
            self._check_compatibility(value)

            values_num = cast(AnyNDArrayLike_IF, self._array_numerical + value.values_num)
            values_str = np.char.add(self._array_string, value.values_str)
            value_name = value.full_name

        elif isinstance(value, (str, np.str_)):
            if self._array_string.size == 0:
                raise ValueError("No string data to add to.")

            values_num = self._array_numerical
            values_str = np.char.add(self._array_string, value)
            value_name = value

        else:
            raise ValueError(f"Cannot add value with unknown type '{type(value)}'.")  # pyright: ignore[reportUnreachable]

        if self.timepoints_column_name is None:
            df_data = pd.concat(
                (
                    pd.DataFrame(
                        np.array(values_num), index=np.array(self._index), columns=np.array(self._columns_numerical)
                    ),
                    pd.DataFrame(
                        np.array(values_str), index=np.array(self._index), columns=np.array(self._columns_string)
                    ),
                ),
                axis=1,
            )

            return tdf.TemporalDataFrame(
                df_data,
                timepoints=self.timepoints_column,
                lock=self.lock,
                name=f"{self.full_name} + {value_name}",
                sort_timepoints=False,
            )

        else:
            df_data = pd.concat(
                (
                    pd.DataFrame(
                        self.timepoints_column_str[:, None],
                        index=np.array(self._index),
                        columns=np.array([str(self.timepoints_column_name)]),
                    ),
                    pd.DataFrame(
                        np.array(values_num), index=np.array(self._index), columns=np.array(self._columns_numerical)
                    ),
                    pd.DataFrame(
                        np.array(values_str), index=np.array(self._index), columns=np.array(self._columns_string)
                    ),
                ),
                axis=1,
            )

            return tdf.TemporalDataFrame(
                df_data,
                timepoints_column_name=self.timepoints_column_name,
                lock=self.lock,
                name=f"{self.full_name} + {value_name}",
                sort_timepoints=False,
            )

    def __add__(self, value: IFS | TemporalDataFrameBase) -> TemporalDataFrame:
        """
        Get a copy with :
            - numerical values incremented by <value> if <value> is a number
            - <value> appended to string values if <value> is a string
        """
        return self._add_core(value)

    def __radd__(self, value: IFS | TemporalDataFrameBase) -> TemporalDataFrame:  # type: ignore[misc]
        """
        Get a copy with :
            - numerical values incremented by <value> if <value> is a number
            - <value> appended to string values if <value> is a string
        """
        return self.__add__(value)

    def _iadd_str(self, value: str) -> TemporalDataFrameBase:
        """Inplace modification of the string values."""
        self._array_string = np.char.add(self._array_string, value)
        return self

    def __iadd__(self, value: IFS | TemporalDataFrameBase) -> TemporalDataFrameBase:
        """
        Modify inplace the values :
            - numerical values incremented by <value> if <value> is a number.
            - <value> appended to string values if <value> is a string.
        """
        if isinstance(value, (str, np.str_)):
            if self._array_string.size == 0:
                raise ValueError("No string data to add to.")

            return self._iadd_str(value)

        elif isinstance(value, (int, float, np.integer, np.floating)):
            if self._array_numerical.size == 0:
                raise ValueError("No numerical data to add to.")

            self._array_numerical += value
            return self

        raise NotImplementedError

    def _op_core(self, value: IF | TemporalDataFrameBase, operation: Literal["sub", "mul", "div"]) -> TemporalDataFrame:
        """
        Internal function for subtracting, multiplying by and dividing by a value, called from __add__. Do not use
        directly.
        """
        if operation == "sub":
            if self._array_numerical.size == 0:
                raise ValueError("No numerical data to subtract.")
            op = "-"

            if isinstance(value, tdf.TemporalDataFrameBase):
                self._check_compatibility(value)

                values_num = self._array_numerical - value.values_num
                value_name = value.full_name

            elif isinstance(value, (int, float, np.integer, np.floating)):  # pyright: ignore[reportUnnecessaryIsInstance]
                values_num = self._array_numerical - value
                value_name = str(value)

            else:
                raise ValueError(f"Cannot subtract value with unknown type '{type(value)}'.")  # pyright: ignore[reportUnreachable]

        elif operation == "mul":
            if self._array_numerical.size == 0:
                raise ValueError("No numerical data to multiply.")
            op = "*"

            if isinstance(value, tdf.TemporalDataFrameBase):
                self._check_compatibility(value)

                values_num = self._array_numerical * value.values_num
                value_name = value.full_name

            elif isinstance(value, (int, float, np.integer, np.floating)):  # pyright: ignore[reportUnnecessaryIsInstance]
                values_num = self._array_numerical * value
                value_name = str(value)

            else:
                raise ValueError(f"Cannot multiply by value with unknown type '{type(value)}'.")  # pyright: ignore[reportUnreachable]

        elif operation == "div":
            if self._array_numerical.size == 0:
                raise ValueError("No numerical data to divide.")
            op = "/"

            if isinstance(value, tdf.TemporalDataFrameBase):
                self._check_compatibility(value)

                with np.errstate(invalid="ignore"):  # NOTE: ignore divide by zero errors and set result as NaN
                    values_num = self._array_numerical / value.values_num
                value_name = value.full_name

            elif isinstance(value, (int, float, np.integer, np.floating)):  # pyright: ignore[reportUnnecessaryIsInstance]
                values_num = self._array_numerical / value
                value_name = str(value)

            else:
                raise ValueError(f"Cannot divide by value with unknown type '{type(value)}'.")  # pyright: ignore[reportUnreachable]

        else:
            raise ValueError(f"Unknown operation '{operation}'.")  # pyright: ignore[reportUnreachable]

        if self.timepoints_column_name is None:
            df_data = pd.concat(
                (
                    pd.DataFrame(
                        np.array(values_num), index=np.array(self._index), columns=np.array(self._columns_numerical)
                    ),
                    pd.DataFrame(
                        np.array(self._array_string),
                        index=np.array(self._index),
                        columns=np.array(self._columns_string),
                    ),
                ),
                axis=1,
            )

            return tdf.TemporalDataFrame(
                df_data,
                timepoints=self.timepoints_column,
                lock=self.lock,
                name=f"{self.full_name} {op} {value_name}",
                sort_timepoints=False,
            )

        else:
            df_data = pd.concat(
                (
                    pd.DataFrame(
                        self.timepoints_column_str[:, None],
                        index=np.array(self._index),
                        columns=[str(self.timepoints_column_name)],
                    ),
                    pd.DataFrame(
                        np.array(values_num), index=np.array(self._index), columns=np.array(self._columns_numerical)
                    ),
                    pd.DataFrame(
                        np.array(self._array_string),
                        index=np.array(self._index),
                        columns=np.array(self._columns_string),
                    ),
                ),
                axis=1,
            )

            return tdf.TemporalDataFrame(
                df_data,
                timepoints_column_name=self.timepoints_column_name,
                lock=self.lock,
                name=f"{self.full_name} {op} {value_name}",
                sort_timepoints=False,
            )

    def __sub__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrame:
        """
        Get a copy with :
            - numerical values decremented by <value>.
        """
        return self._op_core(value, "sub")

    def __rsub__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrame:  # type: ignore[misc]
        """
        Get a copy with :
            - numerical values decremented by <value>.
        """
        return self.__sub__(value)

    def __isub__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrameBase:
        """
        Modify inplace the values :
            - numerical values decremented by <value>.
        """
        if self._array_numerical.size == 0:
            raise ValueError("No numerical data to subtract.")

        if isinstance(value, (int, float, np.integer, np.floating)):
            self._array_numerical -= value  # type: ignore[assignment]
            return self

        raise ValueError(f"Cannot subtract value with unknown type '{type(value)}'.")

    def __mul__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrame:
        """
        Get a copy with :
            - numerical values multiplied by <value>.
        """
        return self._op_core(value, "mul")

    def __rmul__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrame:  # type: ignore[misc]
        """
        Get a copy with :
            - numerical values multiplied by <value>.
        """
        return self.__mul__(value)

    def __imul__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrameBase:
        """
        Modify inplace the values :
            - numerical values multiplied by <value>.
        """
        if self._array_numerical.size == 0:
            raise ValueError("No numerical data to multiply.")

        if isinstance(value, (int, float, np.integer, np.floating)):
            self._array_numerical *= value  # type: ignore[assignment]
            return self

        raise ValueError(f"Cannot subtract value with unknown type '{type(value)}'.")

    def __truediv__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrame:
        """
        Get a copy with :
            - numerical values divided by <value>.
        """
        return self._op_core(value, "div")

    def __rtruediv__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrame:  # type: ignore[misc]
        """
        Get a copy with :
            - numerical values divided by <value>.
        """
        return self.__truediv__(value)

    def __itruediv__(self, value: IF | TemporalDataFrameBase) -> TemporalDataFrameBase:
        """
        Modify inplace the values :
            - numerical values divided by <value>.
        """
        if self._array_numerical.size == 0:
            raise ValueError("No numerical data to divide.")

        if isinstance(value, (int, float, np.integer, np.floating)):
            self._array_numerical /= value  # type: ignore[assignment]
            return self

        raise ValueError(f"Cannot subtract value with unknown type '{type(value)}'.")

    @override
    def __eq__(self, other: Any) -> bool | npt.NDArray[np.bool_]:  # type: ignore[override]
        """
        Test for equality with :
            - another TemporalDataFrame or view of a TemporalDataFrame
            - a single value (either numerical or string)
        """
        if isinstance(other, tdf.TemporalDataFrameBase):
            for attr in [
                "timepoints_column_name",
                "has_locked_indices",
                "has_locked_columns",
                "columns",
                "timepoints_column",
                "index",
                "values_num",
                "values_str",
            ]:
                if not are_equal(getattr(self, attr), getattr(other, attr)):
                    return False

            return True

        if isinstance(other, (int, float, np.number)):
            return cast(npt.NDArray[np.bool_], self._array_numerical == other)

        elif isinstance(other, (str, np.str_)):
            return cast(npt.NDArray[np.bool_], self._array_string == other)

        return False

    @abstractmethod
    def __invert__(self) -> TemporalDataFrameView:
        """
        Invert the getitem selection behavior : all elements NOT present in the slicers will be selected.
        """

    @override
    def __ez_write__(self, grp: ez.EZDict[Any]) -> None:
        if self._data is not None and self._data == grp:
            return

        grp.attrs.put(self._attr_dict)  # pyright: ignore[reportArgumentType]

        grp["timepoints_index"] = self._timepoints_index
        grp["index"] = self._index
        grp["columns_numerical"] = self._columns_numerical
        grp["columns_string"] = self._columns_string
        grp["array_numerical"] = self._array_numerical
        grp["array_string"] = self._array_string

    def __array__(self, dtype: np.dtype | None = None, copy: bool | None = None) -> npt.NDArray[Any]:
        if not copy:
            raise ValueError("converting to a numpy array always creates a copy.")

        return np.array(self.values, dtype=dtype)

    @property
    def name(self) -> str:
        """
        Get the name.
        """
        return str(self._attr_dict["name"])

    @property
    @abstractmethod
    def full_name(self) -> str:
        """
        Get the full name.
        """

    @property
    def data(self) -> ez.EZDict[Any] | None:
        """Get the data backing this TemporalDataFrame."""
        return self._data

    @property
    def lock(self) -> tuple[bool, bool]:
        """
        Get the index and columns lock state.
        """
        return self.has_locked_indices, self.has_locked_columns

    @property
    def shape(self) -> tuple[int, list[int], int]:
        """
        Get the shape of this TemporalDataFrame as a 3-tuple of :
            - number of time-points
            - number of rows per time-point
            - number of columns
        """
        return (
            self.n_timepoints,
            [self._timepoints_index.n_at(tp) for tp in self._timepoints_index],
            self.n_columns_num + self.n_columns_str,
        )

    @property
    def timepoints(self) -> tp.TimePointArray | NDArrayView[tp.TimePoint]:
        """
        Get the list of unique time points in this TemporalDataFrame.
        """
        return self._timepoints_index.timepoints

    @property
    def timepoints_index(self) -> tp.TimePointIndex:
        """
        Get the column of time point values as a TimePointIndex.
        """
        return self._timepoints_index

    @property
    def timepoints_column(self) -> tp.TimePointNArray:
        """
        Get the column of time-point values.
        """
        return self._timepoints_index.as_array()

    @property
    def n_timepoints(self) -> int:
        return len(self._timepoints_index.timepoints)

    @property
    def timepoints_column_str(self) -> npt.NDArray[np.str_]:
        """
        Get the column of time-point values cast as strings.
        """
        return self.timepoints_column.astype(str)

    @property
    def timepoints_column_numerical(self) -> npt.NDArray[np.float64]:
        """
        Get the column of time-point values cast as floats.
        """
        return self.timepoints_column.astype(np.float64)

    @property
    def timepoints_column_name(self) -> str | None:
        """
        Get the name of the column containing the time-points values.
        """
        col_name = self._attr_dict["timepoints_column_name"]
        return None if col_name is None else str(col_name)

    def get_timepoints_column_name(self) -> str:
        return (
            DEFAULT_TIME_COL_NAME
            if self._attr_dict["timepoints_column_name"] is None
            else str(self._attr_dict["timepoints_column_name"])
        )

    @property
    def index(self) -> RepeatingIndex:
        """
        Get the index across all time-points.
        """
        if self._attr_dict["repeating_index"]:
            return RepeatingIndex(self._index[self._timepoints_index.at(self.tp0)], repeats=self.n_timepoints)

        return RepeatingIndex(self._index)

    @index.setter
    def index(self, values: npt.NDArray[np_IFS] | RepeatingIndex) -> None:
        """
        Set the index for rows across all time-points.
        """
        self.set_index(values)

    def index_at(self, timepoint: tp.TimePoint) -> RepeatingIndex:
        """
        Get the index at a given time point.
        """
        return RepeatingIndex(self._index[self._timepoints_index.at(timepoint)])

    @property
    def n_index(self) -> int:
        return self._index.shape[0]

    def n_index_at(self, timepoint: tp.TimePoint) -> int:
        return len(self._timepoints_index.at(timepoint))

    @property
    def columns_num(self) -> npt.NDArray[np_IFS]:
        """
        Get the list of column names for numerical data.
        """
        return np.asarray(self._columns_numerical)

    @columns_num.setter
    def columns_num(self, values: AnyNDArrayLike_IFS) -> None:
        """
        Set the list of column names for numerical data.
        """
        if self.has_locked_columns:
            raise VLockError("Cannot set columns in tdf with locked columns.")

        self._columns_numerical[:] = values

    @property
    def n_columns_num(self) -> int:
        """
        Get the number of numerical data columns.
        """
        return self._columns_numerical.shape[0]

    @property
    def columns_str(self) -> npt.NDArray[np_IFS]:
        """
        Get the list of column names for string data.
        """
        return np.asarray(self._columns_string)

    @columns_str.setter
    def columns_str(self, values: AnyNDArrayLike_IFS) -> None:
        """
        Set the list of column names for string data.
        """
        if self.has_locked_columns:
            raise VLockError("Cannot set columns in tdf with locked columns.")

        self._columns_string[:] = values

    @property
    def n_columns_str(self) -> int:
        """
        Get the number of string data columns.
        """
        return self._columns_string.shape[0]

    @property
    def columns(self) -> npt.NDArray[np_IFS]:
        """Get the list of all column names."""
        return np.concatenate((self._columns_numerical, self._columns_string))

    @columns.setter
    def columns(self, values: npt.NDArray[np_IFS]) -> None:
        """Set new column names."""
        if len(values) != self.n_columns:
            raise ValueError(f"Cannot set {self.n_columns}, {len(values)} provided.")

        self._columns_numerical[:] = values[: self.n_columns_num]
        self._columns_string[:] = values[self.n_columns_num :]

    @property
    def n_columns(self) -> int:
        return self.n_columns_num + self.n_columns_str

    @property
    def values_num(self) -> AnyNDArrayLike_IF:
        """
        Get the numerical data.
        """
        return self._array_numerical

    @values_num.setter
    def values_num(self, values: AnyNDArrayLike_IF) -> None:
        """
        Set the numerical data.
        """
        self._array_numerical[:] = values

    @property
    def values_str(self) -> AnyNDArrayLike[np.str_]:
        """
        Get the string data.
        """
        return self._array_string

    @values_str.setter
    def values_str(self, values: AnyNDArrayLike[np.str_]) -> None:
        """
        Set the string data.
        """
        self._array_string[:] = values

    @property
    def values(self) -> AnyNDArrayLike[np.object_]:
        """
        Get all the data (num and str concatenated).
        """
        if not len(self._columns_string):
            return self._array_numerical

        if not len(self._columns_numerical):
            return self._array_string

        return np.hstack((self._array_numerical.astype(object), self._array_string))

    @property
    def tp0(self) -> tp.TimePoint:
        return self._timepoints_index[0]

    @property
    def at(self) -> VAtIndexer:
        """
        Access a single value from a pair of row and column labels.
        """
        return VAtIndexer(self)

    @property
    def iat(self) -> ViAtIndexer:
        """
        Access a single value from a pair of row and column indices.
        """
        return ViAtIndexer(self)

    @property
    def loc(self) -> VLocIndexer:
        """
        Access a group of rows and columns by label(s) or a boolean array.

        Allowed inputs are:
            - A single label, e.g. 5 or 'a', (note that 5 is interpreted as a label of the index, and never as an
            integer position along the index).
            - A list or array of labels, e.g. ['a', 'b', 'c'].
            - A slice object with labels, e.g. 'a':'f'.
            - A boolean array of the same length as the axis being sliced, e.g. [True, False, True].
            - A callable function with one argument (the calling Series or DataFrame) and that returns valid output
            for indexing (one of the above)
        """
        return VLocIndexer(self)

    @property
    def iloc(self) -> ViLocIndexer:
        """
        Purely integer-location based indexing for selection by position (from 0 to length-1 of the axis).

        Allowed inputs are:
            - An integer, e.g. 5.
            - A list or array of integers, e.g. [4, 3, 0].
            - A slice object with ints, e.g. 1:7.
            - A boolean array.
            - A callable function with one argument (the calling Series or DataFrame) and that returns valid output
            for indexing (one of the above). This is useful in method chains, when you don’t have a reference to the
            calling object, but would like to base your selection on some value.
        """
        return ViLocIndexer(self)

    @property
    def has_locked_indices(self) -> bool:
        """
        Is the "index" axis locked for modification ?
        """
        return bool(self._attr_dict["locked_indices"])

    @property
    def has_locked_columns(self) -> bool:
        """
        Is the "columns" axis locked for modification ?
        """
        return bool(self._attr_dict["locked_columns"])

    @property
    def _empty_numerical(self) -> bool:
        return self._array_numerical.size == 0

    @property
    def _empty_string(self) -> bool:
        return self._array_string.size == 0

    @property
    def empty(self) -> bool:
        """
        Whether this TemporalDataFrame is empty (no numerical data and no string data).
        """
        return self._empty_numerical and self._empty_string

    @property
    @abstractmethod
    def is_view(self) -> bool:
        """
        Is this a view on a TemporalDataFrame ?
        """

    @property
    @abstractmethod
    def is_inverted(self) -> bool:
        """Is this an inverted view on a TemporalDataFrame ?"""

    @property
    def is_backed(self) -> bool:
        """
        Is this TemporalDataFrame backed on a file ?
        """
        return self._data is not None

    @abstractmethod
    def _append_column(self, column_name: IFS, values: npt.NDArray[np_IFS]) -> None:
        pass

    @abstractmethod
    def lock_indices(self) -> None:
        """Lock the "index" axis to prevent modifications."""

    @abstractmethod
    def unlock_indices(self) -> None:
        """Unlock the "index" axis to allow modifications."""

    @abstractmethod
    def lock_columns(self) -> None:
        """Lock the "columns" axis to prevent modifications."""

    @abstractmethod
    def unlock_columns(self) -> None:
        """Unlock the "columns" axis to allow modifications."""

    @abstractmethod
    def set_index(
        self,
        values: Collection[IFS] | RepeatingIndex,
        *,
        force: bool = False,
    ) -> None:
        """Set new index values."""

    @abstractmethod
    def reindex(self, order: npt.NDArray[np_IFS] | RepeatingIndex) -> None:
        """Re-order rows in this TemporalDataFrame so that their index matches the new given order."""

    def _repr_single_array(
        self, tp: tp.TimePoint, n: int, array: AnyNDArrayLike_IFS, columns_: AnyNDArrayLike_IFS
    ) -> tuple[pd.DataFrame, tuple[int, int]]:
        row_indices = self._timepoints_index.at(tp)

        n_rows = len(row_indices)
        n_rows_df = min(n, n_rows)

        n_cols = int(array.shape[1])
        n_cols_df = min(10, n_cols)

        col_indices = np.roll(np.arange(0, n_cols_df) - n_cols_df // 2, -(n_cols_df // 2))

        tp_df = pd.DataFrame(
            np.hstack(
                (
                    np.repeat(tp, n_rows_df).reshape(-1, 1),  # type: ignore[call-overload]
                    np.repeat(VERTICAL_SEPARATOR, n_rows_df).reshape(-1, 1),  # type: ignore[call-overload]
                    np.array(array[np.ix_(row_indices[:n_rows_df], col_indices)]),
                ),
            ),
            index=self._index[row_indices[:n_rows_df]],
            columns=np.hstack((self.get_timepoints_column_name(), "", columns_[col_indices])),
        )

        return tp_df, (n_rows, n_cols)

    def _head_tail(self, n: int) -> str:
        """
        Common function for getting a head or tail representation of this TemporalDataFrame.

        Args:
            n: number of rows to print.

        Returns:
            A short string representation of the first/last n rows in this TemporalDataFrame.
        """
        if not len(self._timepoints_index):
            return f"Time points: []\nColumns: {[col for col in self.columns]}\nIndex: {[idx for idx in self._index]}"

        repr_string = ""

        for timepoint in self.timepoints[:5]:
            timepoint = cast(tp.TimePoint, timepoint)
            # display the first n rows of the first 5 timepoints in this TemporalDataFrame
            repr_string += underlined(f"Time point : {repr(timepoint)}") + "\n"

            if not self._empty_numerical and not self._empty_string:
                first_n_elements = self._timepoints_index.at(timepoint)[:n]
                nb_elements_for_tp = self._timepoints_index.len(timepoint=timepoint)
                one_column_shape = (min(n, nb_elements_for_tp), 1)

                tp_df = pd.DataFrame(
                    np.hstack(
                        (
                            np.tile(timepoint, one_column_shape),  # pyright: ignore[reportCallIssue, reportArgumentType]
                            np.tile(VERTICAL_SEPARATOR, one_column_shape),
                            self._array_numerical[first_n_elements],  # pyright: ignore[reportArgumentType]
                            np.tile(VERTICAL_SEPARATOR, one_column_shape),
                            self._array_string[first_n_elements],  # pyright: ignore[reportArgumentType]
                        )
                    ),
                    index=self._index[first_n_elements],  # pyright: ignore[reportArgumentType]
                    columns=np.hstack(  # pyright: ignore[reportCallIssue]
                        (self.get_timepoints_column_name(), "", self._columns_numerical, "", self._columns_string)  # pyright: ignore[reportArgumentType]
                    ),
                )
                tp_shape: tuple[int, ...] = (
                    nb_elements_for_tp,
                    self._columns_numerical.shape[0] + self._columns_string.shape[0],
                )

            elif not self._empty_numerical:
                tp_df, tp_shape = self._repr_single_array(timepoint, n, self._array_numerical, self._columns_numerical)

            elif not self._empty_string:
                tp_df, tp_shape = self._repr_single_array(timepoint, n, self._array_string, self._columns_string)

            else:
                first_n_elements = self._timepoints_index.at(timepoint)[:n]
                nb_elements_for_tp = self._timepoints_index.len(timepoint=timepoint)
                one_column_shape = (min(n, nb_elements_for_tp), 1)

                tp_df = pd.DataFrame(
                    np.hstack((np.tile(timepoint, one_column_shape), np.tile(VERTICAL_SEPARATOR, one_column_shape))),  # pyright: ignore[reportCallIssue, reportArgumentType]
                    index=self._index[first_n_elements],  # pyright: ignore[reportArgumentType]
                    columns=[self.get_timepoints_column_name(), ""],  # pyright: ignore[reportArgumentType]
                )

                tp_shape = (tp_df.shape[0], 0)

            # remove unwanted shape display by pandas and replace it by our own
            repr_tp_df = repr(tp_df)

            if re.search(r"\n\[.*$", repr_tp_df) is None:
                repr_string += f"{repr_tp_df}\n[{tp_shape[0]} rows x {tp_shape[1]} columns]\n\n"

            else:
                repr_string += re.sub(r"\n\[.*$", f"[{tp_shape[0]} rows x {tp_shape[1]} columns]\n\n", repr_tp_df)

        # then display only the list of remaining timepoints
        if len(self.timepoints) > 5:
            repr_string += f"\nSkipped time points {repr_array(self.timepoints[5:])} ...\n\n\n"

        return repr_string

    def head(self, n: int = 5) -> str:
        """
        Get a short representation of the first n rows in this TemporalDataFrame.

        Args:
            n: number of rows to print.

        Returns:
            A short string representation of the first n rows in this TemporalDataFrame.
        """
        return self._head_tail(n)

    def tail(self, n: int = 5) -> str:
        """
        Get a short representation of the last n rows in this TemporalDataFrame.

        Args:
            n: number of rows to print.

        Returns:
            A short string representation of the last n rows in this TemporalDataFrame.
        """
        # TODO : negative n not handled
        return self._head_tail(-n)

    def _min_max_mean(
        self, func: Literal["min", "max", "mean"], axis: int | None = None
    ) -> float | pd.DataFrame | TemporalDataFrame:
        np_func = getattr(np, func)

        if axis is None:
            return float(np_func(self._array_numerical))

        elif axis == 0:
            if not self._attr_dict["repeating_index"]:
                raise ValueError(f"Can't take '{func}' along axis 0 if indices are not the same at all time-points.")

            return pd.DataFrame(
                np_func(
                    [
                        self._array_numerical[self._timepoints_index.where(timepoint), :]
                        for timepoint in self._timepoints_index
                    ],
                    axis=0,
                ),
                index=self.index_at(self.tp0),
                columns=np.array(self._columns_numerical),
            )

        elif axis == 1:
            return tdf.TemporalDataFrame(
                data=pd.DataFrame(
                    [
                        np_func(self._array_numerical[self._timepoints_index.where(timepoint), :], axis=0)
                        for timepoint in self._timepoints_index
                    ],
                    index=np.repeat(func, self.n_timepoints),
                    columns=np.array(self._columns_numerical),
                ),
                timepoints=self.timepoints,
                timepoints_column_name=self.timepoints_column_name,
            )

        elif axis == 2:
            return tdf.TemporalDataFrame(
                data=pd.DataFrame(
                    np_func(self._array_numerical, axis=1),
                    index=np.array(self._index),
                    columns=[func],
                ),
                timepoints=self.timepoints_column,
                timepoints_column_name=self.timepoints_column_name,
            )

        raise ValueError(f"Invalid axis '{axis}', should be in [0, 1, 2].")

    min = partialmethod(_min_max_mean, func="min")
    max = partialmethod(_min_max_mean, func="max")
    mean = partialmethod(_min_max_mean, func="mean")

    def iterrows(self) -> Generator[tuple[str, tp.TimePoint, pd.Series], None, None]:
        for index, timepoint, num_row, str_row in zip(
            self.index, self.timepoints_column, self._array_numerical, self._array_string
        ):
            yield index, timepoint, pd.Series([*num_row, *str_row])

    def to_dict(
        self, orient: Literal["dict", "list", "series", "split", "tight", "records", "index"] = "dict"
    ) -> dict[str, Any] | list[dict[str, Any]]:
        match orient:
            case "dict":
                return {
                    col: {index: value for index, value in zip(self.index, row)}
                    for col, row in zip(self.columns, self.values.T)
                }

            case "records":
                return [{col: value for col, value in zip(self.columns, row)} for row in self.values]

            case _:
                raise ValueError(f"orient '{orient}' not understood")

    def _convert_to_pandas(
        self,
        with_timepoints: str | None = None,
        timepoints_type: Literal["string", "numerical"] = "string",
        str_index: bool = False,
    ) -> pd.DataFrame:
        """
        Internal function for converting to a pandas DataFrame. Do not use directly, it is called by '.to_pandas()'.

        Args:
            with_timepoints: Name of the column containing time-points data to add to the DataFrame. If left to None,
                no column is created.
            timepoints_type: if <with_timepoints> if True, type of the timepoints that will be added (either 'string'
                or 'numerical'). (default: 'string')
            str_index: cast index as string ?
        """
        index_ = np.array(self._index.astype(str) if str_index else self._index)

        if with_timepoints is None:
            return pd.concat(
                (
                    pd.DataFrame(
                        np.array(self._array_numerical) if self._array_numerical.size else None,
                        index=index_,
                        columns=np.array(self._columns_numerical),
                    ),
                    pd.DataFrame(
                        np.array(self._array_string) if self._array_string.size else None,
                        index=index_,
                        columns=np.array(self._columns_string),
                    ),
                ),
                axis=1,
            )

        if timepoints_type == "string":
            return pd.concat(
                (
                    pd.DataFrame(
                        self.timepoints_column_str[:, None], index=index_, columns=np.array([str(with_timepoints)])
                    ),
                    pd.DataFrame(
                        np.array(self._array_numerical) if self._array_numerical.size else None,
                        index=index_,
                        columns=np.array(self._columns_numerical),
                    ),
                    pd.DataFrame(
                        np.array(self._array_string) if self._array_string.size else None,
                        index=index_,
                        columns=np.array(self._columns_string),
                    ),
                ),
                axis=1,
            )

        if timepoints_type == "numerical":
            return pd.concat(
                (
                    pd.DataFrame(
                        self.timepoints_column_numerical[:, None],
                        index=index_,
                        columns=np.array([str(with_timepoints)]),
                    ),
                    pd.DataFrame(
                        np.array(self._array_numerical) if self._array_numerical.size else None,
                        index=index_,
                        columns=np.array(self._columns_numerical),
                    ),
                    pd.DataFrame(
                        np.array(self._array_string) if self._array_numerical.size else None,
                        index=index_,
                        columns=np.array(self._columns_string),
                    ),
                ),
                axis=1,
            )

        raise ValueError(f"Invalid timepoints_type argument '{timepoints_type}'. Should be 'string' or 'numerical'.")  # pyright: ignore[reportUnreachable]

    def to_pandas(
        self,
        with_timepoints: str | None = None,
        timepoints_type: Literal["string", "numerical"] = "string",
        str_index: bool = False,
    ) -> pd.DataFrame:
        """
        Convert to a pandas DataFrame.

        Args:
            with_timepoints: Name of the column containing time-points data to add to the DataFrame. If left to None,
                no column is created.
            timepoints_type: if <with_timepoints> if True, type of the timepoints that will be added (either 'string'
                or 'numerical'). (default: 'string')
            str_index: cast index as string ?
        """
        return self._convert_to_pandas(
            with_timepoints=with_timepoints, timepoints_type=timepoints_type, str_index=str_index
        )

    def write(
        self,
        store: StoreLike,  # pyright: ignore[reportUnknownParameterType]
        *,
        name: str | None = None,
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Save this object to a local file system.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the object, to use inside the store.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store where the object will be saved.
            overwrite: overwrite object if a group with name `name` already exists ? (default: False)
        """
        grp = zarr.open_group(store, path=path, mode=mode)
        if name is not None:
            grp = grp.require_group(name, overwrite=overwrite)

        data: ez.EZDict[Any] = ez.EZDict(grp)
        self.__ez_write__(data)

        if not self.is_backed:
            self._attr_dict = parse_data_h5(data, self.lock, self.name)
            self._index = cast(AnyNDArrayLike_IFS, data["index"])
            self._timepoints_index = cast(tp.TimePointIndex, data["timepoints_index"])
            self._array_numerical = cast(AnyNDArrayLike_IF, data["array_numerical"])
            self._array_string = cast(AnyNDArrayLike[np.str_], data["array_string"])
            self._columns_numerical = cast(AnyNDArrayLike_IFS, data["columns_numerical"])
            self._columns_string = cast(AnyNDArrayLike_IFS, data["columns_string"])
            self._data = data

    def to_csv(
        self, path: str | Path, sep: str = ",", na_rep: str = "", index: bool = True, header: bool = True
    ) -> None:
        """
        Save this TemporalDataFrame in a csv file.

        Args:
            path: a path to the csv file.
            sep: String of length 1. Field delimiter for the output file.
            na_rep: Missing data representation.
            index: Write row names (index) ?
            header: Write out the column names ? If a list of strings is given it is assumed to be aliases for the
                column names.
        """
        self.to_pandas(with_timepoints=self.get_timepoints_column_name()).to_csv(
            path, sep=sep, na_rep=na_rep, index=index, header=header
        )

    def copy(self, deep: bool = True) -> TemporalDataFrame:
        """
        Get a copy.
        """
        if not deep:
            return self

        if self.timepoints_column_name is None:
            return tdf.TemporalDataFrame(
                self.to_pandas(),
                timepoints=self.timepoints_column,
                lock=self.lock,
                name=f"copy of {self.name}",
            )

        return tdf.TemporalDataFrame(
            self.to_pandas(with_timepoints=self.timepoints_column_name),
            timepoints_column_name=self.timepoints_column_name,
            lock=self.lock,
            name=f"copy of {self.name}",
        )

    @abstractmethod
    def merge(self, other: TemporalDataFrame, name: str | None = None) -> TemporalDataFrame:
        """
        Merge two TemporalDataFrames together, by rows. The column names and time points must match.

        Args:
            other: a TemporalDataFrame to merge with this one.
            name: a name for the merged TemporalDataFrame.

        Returns:
            A new merged TemporalDataFrame.
        """
