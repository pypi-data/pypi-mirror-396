from __future__ import annotations

from collections.abc import Collection, Iterable, Iterator
from typing import TYPE_CHECKING, Any, SupportsIndex, cast, overload, override

import ch5mpy.indexing as ci
import numpy as np
import numpy.typing as npt
from numpy._typing import _ArrayLikeObject_co  # pyright: ignore[reportPrivateUsage]

if TYPE_CHECKING:
    from vdata._typing import Indexer
    from vdata.timepoint import TimePoint

_RESERVED_ATTRIBUTES = frozenset(
    (
        "_array",
        "_index",
        "_exposed_attr",
        "size",
        "shape",
        "dtype",
        "array_type",
    )
)


class NDArrayView[T: np.generic | TimePoint](Collection[T]):
    """View on a numpy ndarray that can be subsetted infinitely without copying."""

    __slots__: tuple[str, ...] = "_array", "_index", "_exposed_attr"

    def __init__(
        self,
        array: ArrayGetter[T],
        index: Indexer | tuple[Indexer, ...] | ci.Selection,
        exposed_attributes: Iterable[str] = (),
    ) -> None:
        self._array: ArrayGetter[T] = array
        self._index: ci.Selection = (
            index if isinstance(index, ci.Selection) else ci.Selection.from_selector(index, array.get().shape)
        )
        self._exposed_attr: frozenset[str] = frozenset(exposed_attributes)

        if not self._exposed_attr.isdisjoint(_RESERVED_ATTRIBUTES):
            raise ValueError(
                f"Cannot expose reserved attributes : {_RESERVED_ATTRIBUTES.intersection(self._exposed_attr)}."
            )

    @override
    def __repr__(self) -> str:
        return repr(self._view()) + "*"

    def __array__(self, dtype: npt.DTypeLike = None, copy: bool | None = None) -> npt.NDArray[Any]:
        if dtype is None:
            return self._view(copy=copy)

        return self._view(copy=copy).astype(dtype)

    @override
    def __getattribute__(self, key: str) -> Any:
        if key in object.__getattribute__(self, "_exposed_attr"):
            return getattr(self._array.get(), key)

        return super().__getattribute__(key)

    @overload
    def __getitem__(self, index: SupportsIndex | tuple[SupportsIndex, ...]) -> T: ...
    @overload
    def __getitem__(
        self,
        index: slice
        | npt.NDArray[np.integer]
        | npt.NDArray[np.bool_]
        | None
        | tuple[slice | npt.NDArray[np.integer] | npt.NDArray[np.bool_] | None, ...],
    ) -> NDArrayView[T]: ...
    @override
    def __getitem__(self, index: Indexer | tuple[Indexer, ...]) -> NDArrayView[T] | T:
        sel = ci.Selection.from_selector(index, self.shape).cast_on(self._index)

        if np.prod(sel.out_shape) == 1:
            return cast(T, self._array.get()[sel.get_indexers()])  # pyright: ignore[reportInvalidCast]

        return NDArrayView(self._array, sel, exposed_attributes=self._exposed_attr)

    def __setitem__(self, index: Indexer, values: Any) -> None:
        sel = ci.Selection.from_selector(index, self.shape).cast_on(self._index)

        self._array.get()[sel.get_indexers()] = values

    @override
    def __len__(self) -> int:
        return len(self._view())

    @override
    def __contains__(self, key: Any) -> bool:
        return key in self._view()

    @override
    def __iter__(self) -> Iterator[T]:
        return iter(self._view())

    @override
    def __eq__(self, __value: object) -> npt.NDArray[np.bool_]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._view().__eq__(__value)

    def __lt__(self, __value: _ArrayLikeObject_co) -> npt.NDArray[np.bool_]:
        return self._view().__lt__(__value)

    def __le__(self, __value: _ArrayLikeObject_co) -> npt.NDArray[np.bool_]:
        return self._view().__le__(__value)

    def __gt__(self, __value: _ArrayLikeObject_co) -> npt.NDArray[np.bool_]:
        return self._view().__gt__(__value)

    def __ge__(self, __value: _ArrayLikeObject_co) -> npt.NDArray[np.bool_]:
        return self._view().__ge__(__value)

    def __add__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() + other)

    def __sub__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() - other)

    def __mul__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() * other)

    def __truediv__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() / other)

    def __pow__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() ** other)

    @property
    def size(self) -> int:
        return self._view().size

    @property
    def shape(self) -> tuple[int, ...]:
        return self._view().shape

    @property
    def dtype(self) -> np.dtype[Any]:
        return self._view().dtype

    @property
    def array_type(self) -> type[Any]:
        return type(self._array.get())  # pyright: ignore[reportUnknownVariableType]

    def _view(self, copy: bool | None = None) -> npt.NDArray[Any]:
        array = cast(npt.NDArray[Any], self._array.get()[self._index.get_indexers()])

        if copy:
            return np.array(array)

        return array

    def copy(self) -> npt.NDArray[Any]:
        return self._view().copy()

    def astype(self, dtype: npt.DTypeLike) -> npt.NDArray[Any]:
        return self._view().astype(dtype)

    def min(
        self, axis: int | tuple[int, ...] | None = None, out: npt.NDArray[Any] | None = None
    ) -> T | npt.NDArray[Any]:
        return self._view().min(axis=axis, out=out)

    def max(
        self, axis: int | tuple[int, ...] | None = None, out: npt.NDArray[Any] | None = None
    ) -> T | npt.NDArray[Any]:
        return self._view().max(axis=axis, out=out)

    def mean(
        self,
        axis: int | tuple[int, ...] | None = None,
        dtype: npt.DTypeLike | None = None,
        out: npt.NDArray[Any] | None = None,
    ) -> T | npt.NDArray[Any]:
        return self._view().mean(axis=axis, dtype=dtype, out=out)  # type: ignore[no-any-return, misc, arg-type]

    def flatten(self) -> npt.NDArray[Any]:
        return self._view().flatten()


class ArrayGetter[T: np.generic | TimePoint]:
    def __init__(self, container: Any, name: str):
        self._container: Any = container
        self._name: str = name

    def get(self) -> npt.NDArray[T]:  # pyright: ignore[reportInvalidTypeForm, reportUnknownParameterType]
        return getattr(self._container, self._name)  # type: ignore[no-any-return]
