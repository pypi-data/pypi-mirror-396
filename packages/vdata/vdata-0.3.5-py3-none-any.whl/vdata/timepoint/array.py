from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable, Iterator, Mapping
from dataclasses import dataclass
from functools import partial
from types import EllipsisType
from typing import TYPE_CHECKING, Any, Callable, Literal, SupportsIndex, cast, final, overload, override

import ezarr
import ezarr as ez
import numpy as np
import numpy.typing as npt
import zarr
from numpy import _NoValue as NoValue  # pyright: ignore[reportAttributeAccessIssue, reportUnknownVariableType]
from numpy._globals import _CopyMode
from numpy._typing import _ArrayLikeInt_co  # pyright: ignore[reportPrivateUsage]
from numpy._typing import _NumberLike_co as NumberLike_co  # pyright: ignore[reportPrivateUsage]
from numpy._typing import _ShapeLike as ShapeLike  # pyright: ignore[reportPrivateUsage]
from zarr.core.array import (
    DEFAULT_FILL_VALUE,
    CompressorsLike,
    FiltersLike,
    SerializerLike,
    ShardsLike,
    create_array,  # pyright: ignore[reportUnknownVariableType]
)
from zarr.core.array_spec import ArrayConfigLike
from zarr.core.chunk_key_encodings import ChunkKeyEncodingLike
from zarr.core.common import JSON, DimensionNames, MemoryOrder, ZarrFormat
from zarr.core.common import ShapeLike as zShapeLike
from zarr.core.dtype import ZDTypeLike
from zarr.core.sync import sync
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]

from vdata.array_view import NDArrayView
from vdata.timepoint._functions import HANDLED_FUNCTIONS
from vdata.timepoint._typing import TIME_UNIT, TimePointLike
from vdata.timepoint.range import TimePointRange
from vdata.timepoint.timepoint import TIME_UNIT_ORDER, TimePoint
from vdata.utils import isCollection


def _add_unit(match: re.Match[Any], unit: TIME_UNIT) -> str:
    number = str(match.group(0))
    if number.endswith("."):
        number += "0"
    return number + unit


@dataclass(repr=False)
class TimePointArray(ABC, ezarr.SupportsEZReadWrite):
    _unit: TIME_UNIT

    @override
    def __repr__(self) -> str:
        if self.size:
            return f"{type(self).__name__}({re.sub(rf'{self._unit} ', rf'{self._unit}, ', str(self))})"

        return f"{type(self).__name__}({re.sub(rf'{self._unit} ', rf'{self._unit}, ', str(self))}, unit={self._unit})"

    @override
    def __str__(self) -> str:
        return re.sub(r"(\d+(\.\d*)?|\d+)", partial(_add_unit, unit=self._unit), str(self.__array__()))

    @abstractmethod
    def __array__(self) -> np.ndarray: ...

    @abstractmethod
    def __len__(self) -> int: ...

    if TYPE_CHECKING:

        def __iter__(self) -> Iterator[TimePoint]: ...

    @overload
    def __getitem__(self, key: SupportsIndex) -> TimePoint: ...
    @overload
    def __getitem__(
        self,
        key: (
            npt.NDArray[np.integer[Any]]
            | npt.NDArray[np.bool_]
            | tuple[npt.NDArray[np.integer[Any]] | npt.NDArray[np.bool_], ...]
            | None
            | slice
            | EllipsisType
            | _ArrayLikeInt_co
            | tuple[None | slice | EllipsisType | _ArrayLikeInt_co | SupportsIndex, ...]
        ),
    ) -> TimePointNArray: ...
    def __getitem__(
        self,
        key: (
            SupportsIndex
            | npt.NDArray[np.integer[Any]]
            | npt.NDArray[np.bool_]
            | tuple[npt.NDArray[np.integer[Any]] | npt.NDArray[np.bool_], ...]
            | None
            | slice
            | EllipsisType
            | _ArrayLikeInt_co
            | tuple[None | slice | EllipsisType | _ArrayLikeInt_co | SupportsIndex, ...]
        ),
    ) -> TimePoint | TimePointNArray: ...

    def __contains__(self, value: TimePointLike) -> bool:
        value = TimePoint(value)

        if value.unit != self.unit:
            return False

        return bool(np.isin(value.value, self))

    @classmethod
    @override
    def __ez_read__(cls, grp: ez.EZDict[Any]) -> TimePointZArray:
        array = grp.group._sync(grp.group._async_group.getitem("array"))  # pyright: ignore[reportPrivateUsage]
        assert isinstance(array, zarr.AsyncArray)

        unit: TIME_UNIT = cast(TIME_UNIT, grp.attrs["unit"])
        assert unit in ["s", "m", "h", "D", "M", "Y"]

        return TimePointZArray(unit, array)

    @override
    def __ez_write__(self, grp: ez.EZDict[Any]) -> None:
        grp.attrs["unit"] = self._unit
        grp["array"] = np.array(self)

    @property
    @abstractmethod
    def size(self) -> int: ...

    @property
    def unit(self) -> TIME_UNIT:
        return self._unit

    def astype(
        self,
        dtype: npt.DTypeLike,
        order: np._OrderKACF = "K",  # pyright: ignore[reportPrivateUsage]
        casting: np._CastingKind = "unsafe",  # pyright: ignore[reportPrivateUsage]
        subok: bool = True,
        copy: bool | _CopyMode = True,
    ) -> npt.NDArray[Any]:
        del order, casting, subok

        if not copy:
            raise ValueError("astype() casting always creates a copy.")

        if np.issubdtype(dtype, str):
            return np.char.add(np.array(self, dtype=dtype), self._unit)

        return np.array(self, dtype=dtype)

    def min(
        self,
        /,
        axis: ShapeLike | None = None,
        out: np.ndarray | None = None,
        keepdims: bool = False,
        initial: NumberLike_co = NoValue,
        where: bool | npt.NDArray[np.bool_] = True,
    ) -> TimePoint:
        del axis, out, keepdims
        return TimePoint(np.min(np.array(self), initial=initial, where=where), unit=self._unit)

    def max(
        self,
        /,
        axis: ShapeLike | None = None,
        out: np.ndarray | None = None,
        keepdims: bool = False,
        initial: NumberLike_co = NoValue,
        where: bool | npt.NDArray[np.bool_] = True,
    ) -> TimePoint:
        del axis, out, keepdims
        return TimePoint(np.max(np.array(self), initial=initial, where=where), unit=self._unit)

    def mean(
        self,
        /,
        axis: ShapeLike | None = None,
        dtype: npt.DTypeLike = None,
        out: np.ndarray | None = None,
        keepdims: bool = False,
        where: bool | npt.NDArray[np.bool_] = True,
    ) -> TimePoint:
        del axis, dtype, out, keepdims
        return TimePoint(np.mean(np.array(self), where=where), unit=self._unit)

    def to_list(self) -> list[TimePoint]:
        return [tp for tp in self]


@final
@dataclass(repr=False)
class TimePointZArray(zarr.Array, TimePointArray):
    @classmethod
    def from_array(cls, arr: npt.NDArray[np.number], unit: TIME_UNIT = "h") -> TimePointZArray:
        return create_timepointarray({}, unit=unit, data=arr)

    __repr__ = TimePointArray.__repr__  # pyright: ignore[reportAssignmentType]
    __str__ = TimePointArray.__str__

    @override
    def __len__(self) -> int:
        return self.size

    @overload
    def __getitem__(self, key: int) -> TimePoint: ...
    @overload
    def __getitem__(
        self,
        key: slice | EllipsisType | list[int] | npt.NDArray[np.intp] | npt.NDArray[np.bool_],
    ) -> TimePointNArray: ...
    @override
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, key: int | slice | EllipsisType | list[int] | npt.NDArray[np.intp] | npt.NDArray[np.bool_]
    ) -> TimePoint | TimePointNArray:
        res = super().__getitem__(key)
        if isinstance(res, np.ndarray):
            if res.ndim == 0:
                return TimePoint(cast(np.floating, res[()]), unit=self._unit)  # pyright: ignore[reportArgumentType, reportCallIssue]

            return TimePointNArray(res, unit=self._unit)  # pyright: ignore[reportArgumentType]

        return TimePoint(cast(np.floating, res), unit=self._unit)

    @override
    def __eq__(self, other: object) -> bool:
        return np.equal(self[:], other)  # pyright: ignore[reportCallIssue, reportUnknownVariableType, reportArgumentType]

    astype = TimePointArray.astype
    min = TimePointArray.min
    max = TimePointArray.max
    mean = TimePointArray.mean
    to_list = TimePointArray.to_list


@final
class TimePointNArray(np.ndarray, TimePointArray):  # pyright: ignore[reportIncompatibleMethodOverride]
    __repr__ = TimePointArray.__repr__
    __str__ = TimePointArray.__str__

    def __new__(
        cls, arr: Collection[int | float | np.integer | np.floating], /, *, unit: TIME_UNIT | None = None
    ) -> TimePointNArray:
        if isinstance(arr, TimePointNArray):
            unit = arr.unit

        np_arr: TimePointNArray = np.asarray(arr, dtype=np.float64).view(cls)
        np_arr._unit = unit or "h"
        return np_arr

    def __init__(self, arr: Collection[int | float | np.integer | np.floating], /, *, unit: TIME_UNIT | None = None):
        super().__init__(unit or "h")

    @override
    def __array_finalize__(self, obj: npt.NDArray[np.float64] | None) -> None:
        if self.ndim == 0:
            self.shape: list[int] = [1]

        if obj is not None:
            self._unit: TIME_UNIT = getattr(obj, "_unit", "h")

    @override
    def __array_ufunc__(self, ufunc: np.ufunc, method: str, *inputs: Any, **kwargs: Any) -> Any:
        if ufunc in HANDLED_FUNCTIONS:
            return HANDLED_FUNCTIONS[ufunc](*inputs, **kwargs)

        _inputs = (np.array(i) if isinstance(i, TimePointNArray) else i for i in inputs)
        _kwargs = {k: np.array(v) if isinstance(v, TimePointNArray) else v for k, v in kwargs.items()}

        return getattr(ufunc, method)(*_inputs, **_kwargs)

    @override
    def __array_function__(
        self,
        func: Callable[..., Any],
        types: Iterable[type],
        args: Iterable[Any],
        kwargs: Mapping[str, Any],
    ) -> Any:
        if func not in HANDLED_FUNCTIONS:
            return super().__array_function__(func, types, args, kwargs)

        return HANDLED_FUNCTIONS[func](*args, **kwargs)

    @overload
    def __getitem__(self, key: SupportsIndex) -> TimePoint: ...
    @overload
    def __getitem__(
        self,
        key: (
            npt.NDArray[np.integer[Any]]
            | npt.NDArray[np.bool_]
            | tuple[npt.NDArray[np.integer[Any]] | npt.NDArray[np.bool_], ...]
            | None
            | slice
            | EllipsisType
            | _ArrayLikeInt_co
            | tuple[None | slice | EllipsisType | _ArrayLikeInt_co | SupportsIndex, ...]
        ),
    ) -> TimePointNArray: ...
    @override
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        key: (
            SupportsIndex
            | npt.NDArray[np.integer[Any]]
            | npt.NDArray[np.bool_]
            | tuple[npt.NDArray[np.integer[Any]] | npt.NDArray[np.bool_], ...]
            | None
            | slice
            | EllipsisType
            | _ArrayLikeInt_co
            | tuple[None | slice | EllipsisType | _ArrayLikeInt_co | SupportsIndex, ...]
        ),
    ) -> TimePoint | TimePointNArray:
        res = super().__getitem__(key)
        if isinstance(res, TimePointNArray):
            return res

        return TimePoint(cast(np.floating, res), unit=self._unit)  # pyright: ignore[reportInvalidCast]

    astype = TimePointArray.astype  # pyright: ignore[reportAssignmentType]
    min = TimePointArray.min  # pyright: ignore[reportAssignmentType]
    max = TimePointArray.max  # pyright: ignore[reportAssignmentType]
    mean = TimePointArray.mean  # pyright: ignore[reportAssignmentType]
    to_list = TimePointArray.to_list


@overload
def atleast_1d(obj: TimePointNArray) -> TimePointNArray: ...
@overload
def atleast_1d(obj: NDArrayView[TimePoint]) -> NDArrayView[TimePoint]: ...
@overload
def atleast_1d(
    obj: Collection[int | float | np.integer | np.floating] | int | float | np.integer | np.floating,
) -> TimePointNArray: ...
def atleast_1d(
    obj: TimePointNArray
    | NDArrayView[TimePoint]
    | Collection[int | float | np.integer | np.floating]
    | int
    | float
    | np.integer
    | np.floating,
) -> TimePointNArray | NDArrayView[TimePoint]:
    if isinstance(obj, TimePointNArray) or (isinstance(obj, NDArrayView) and obj.array_type == TimePointNArray):
        return obj

    if isinstance(obj, Collection):
        return TimePointNArray(obj)

    return TimePointNArray([obj])


def create_timepointarray(
    store: StoreLike,  # pyright: ignore[reportUnknownParameterType]
    *,
    unit: TIME_UNIT,
    name: str | None = None,
    shape: zShapeLike | None = None,
    dtype: ZDTypeLike | None = None,
    data: np.ndarray[Any, np.dtype[Any]] | None = None,
    chunks: tuple[int, ...] | Literal["auto"] = "auto",
    shards: ShardsLike | None = None,
    filters: FiltersLike = "auto",
    compressors: CompressorsLike = "auto",
    serializer: SerializerLike = "auto",
    fill_value: Any | None = DEFAULT_FILL_VALUE,
    order: MemoryOrder | None = None,
    zarr_format: ZarrFormat | None = 3,
    attributes: dict[str, JSON] | None = None,
    chunk_key_encoding: ChunkKeyEncodingLike | None = None,
    dimension_names: DimensionNames = None,
    storage_options: dict[str, Any] | None = None,
    overwrite: bool = False,
    config: ArrayConfigLike | None = None,
    write_data: bool = True,
):
    return TimePointZArray(
        unit,
        sync(
            create_array(
                store,
                name=name,
                shape=shape,
                dtype=dtype,
                data=data,
                chunks=chunks,
                shards=shards,
                filters=filters,
                compressors=compressors,
                serializer=serializer,
                fill_value=fill_value,
                order=order,
                zarr_format=zarr_format,
                attributes=attributes,
                chunk_key_encoding=chunk_key_encoding,
                dimension_names=dimension_names,
                storage_options=storage_options,
                overwrite=overwrite,
                config=config,
                write_data=write_data,
            )
        ),
    )


def as_timepointarray(time_list: Any, /, *, unit: TIME_UNIT | None = None) -> TimePointNArray | NDArrayView[TimePoint]:
    r"""
    Args:
        time_list: a list for timepoints (TimePointArray, TimePointRange, object or collection of objects).
        unit: enforce a time unit. /!\ replaces any unit found in `time_list`.
    """
    if isinstance(time_list, TimePointArray) or (
        isinstance(time_list, NDArrayView) and time_list.array_type == TimePointArray
    ):
        return time_list  # pyright: ignore[reportReturnType]

    if isinstance(time_list, TimePointRange):
        return TimePointNArray(
            np.arange(float(time_list.start), float(time_list.stop), float(time_list.step)), unit=time_list.unit
        )

    if not isCollection(time_list):
        time_list = [time_list]
    time_list = np.asarray(time_list)

    if not time_list.size or np.issubdtype(time_list.dtype, np.floating) or np.issubdtype(time_list.dtype, np.integer):
        return TimePointNArray(time_list, unit=unit)

    if np.issubdtype(time_list.dtype, str):
        unique_units = np.unique([e[-1] for e in time_list])

        if len(unique_units) == 1 and unique_units[0] in {"s", "m", "h", "D", "M", "Y"}:
            dtype = f"<U{int(time_list.dtype.str.split('U')[1]) - 1}"
            try:
                return TimePointNArray(time_list.astype(dtype), unit=unique_units[0] if unit is None else unit)

            except ValueError:
                pass

    if unit is not None:
        return TimePointNArray([TimePoint(tp, unit=unit).value_as(unit) for tp in np.atleast_1d(time_list)], unit=unit)

    _timepoint_list = [TimePoint(tp) for tp in np.atleast_1d(time_list)]
    _largest_unit = sorted(np.unique([tp.unit for tp in _timepoint_list]), key=lambda u: TIME_UNIT_ORDER[u])[0]

    try:
        return TimePointNArray([tp.value_as(_largest_unit) for tp in _timepoint_list], unit=_largest_unit)

    except ValueError as e:
        raise TypeError(
            f"Unexpected type '{type(time_list)}' for 'time_list', should be a collection of time-points."
        ) from e
