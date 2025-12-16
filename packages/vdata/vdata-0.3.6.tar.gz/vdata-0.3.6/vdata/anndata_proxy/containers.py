from __future__ import annotations

import operator as op
from collections.abc import (
    Collection,
    ItemsView,
    KeysView,
    MutableMapping,
    ValuesView,
)
from functools import partialmethod
from typing import (
    Any,
    Callable,
    ClassVar,
    cast,
    final,
    override,
)

import numpy as np
import numpy.typing as npt
import pandas as pd
import scipy.sparse as ss
from ezarr.dataframe import EZDataFrame

import vdata
from vdata._typing import IFS, AnyNDArrayLike
from vdata.tdf import TemporalDataFrame, TemporalDataFrameBase
from vdata.tdf.index import RepeatingIndex

type _NP_IF = np.integer | np.floating


class TemporalDataFrameContainerProxy:
    __slots__: tuple[str, ...] = "_vdata", "_tdfs", "_name", "_columns"

    def __init__(self, vdata: vdata.VData | vdata.VDataView, name: str, columns: Collection[IFS] | None) -> None:
        self._vdata: vdata.VData | vdata.VDataView = vdata
        self._tdfs: MutableMapping[str, TemporalDataFrameBase] = getattr(vdata, name)
        self._name: str = name.capitalize()
        self._columns: Collection[IFS] | None = columns

    @override
    def __repr__(self) -> str:
        return f"{self._name} with keys: {', '.join(self._tdfs.keys())}"

    def __getitem__(self, key: str) -> ArrayStack2DProxy:
        return ArrayStack2DProxy(self._tdfs[str(key)].values_num, self._tdfs[str(key)].values_str, str(key))

    def __setitem__(self, key: str, value: npt.NDArray[Any]) -> None:
        self._tdfs[key] = TemporalDataFrame(
            value,
            index=self._vdata.obs.index,
            columns=self._columns,
            timepoints=self._vdata.obs.timepoints_column,
        )

    def __delitem__(self, key: str) -> None:
        del self._tdfs[str(key)]

    def __contains__(self, key: str) -> bool:
        return key in self.keys()

    def keys(self) -> KeysView[str]:
        return self._tdfs.keys()

    def values(self) -> ValuesView[TemporalDataFrameBase]:
        return self._tdfs.values()

    def items(self) -> ItemsView[str, TemporalDataFrameBase]:
        return self._tdfs.items()


class ArrayStack2DProxy:
    __slots__: tuple[str, ...] = "_array_numeric", "_array_string", "layer_name"
    ndim: ClassVar[int] = 2

    def __init__(
        self, array_numeric: AnyNDArrayLike[_NP_IF], array_string: AnyNDArrayLike[np.str_], layer_name: str | None
    ) -> None:
        self._array_numeric: AnyNDArrayLike[_NP_IF] | None = array_numeric if array_numeric.size else None
        self._array_string: AnyNDArrayLike[_NP_IF] | None = array_string if array_string.size else None
        self.layer_name: str | None = layer_name

    @override
    def __repr__(self) -> str:
        return repr(self.stack(n=5)) + "\n..." if self.shape[1] > 5 else ""

    def __getitem__(self, item: Any) -> Any:
        if self._array_numeric is not None and self._array_string is not None:
            return np.hstack((self._array_numeric.astype(object), self._array_string))[item]

        if self._array_numeric is None and self._array_string is not None:
            return self._array_string[item]

        if self._array_numeric is not None and self._array_string is None:
            return self._array_numeric[item]

        return np.empty((0, 0))[item]

    def _op(self, other: Any, operation: Callable[[Any, Any], Any]) -> npt.NDArray[_NP_IF]:
        if self._array_string is not None:
            raise TypeError(f"Cannot apply {operation.__name__} with string array.")

        if self._array_numeric is None:
            return np.empty((0, 0))

        return cast(npt.NDArray[_NP_IF], operation(self._array_numeric, other))

    __add__ = __radd__ = partialmethod(_op, operation=op.add)  # pyright: ignore[reportUnannotatedClassAttribute]
    __sub__ = __rsub__ = partialmethod(_op, operation=op.sub)  # pyright: ignore[reportUnannotatedClassAttribute]
    __mul__ = __rmul__ = partialmethod(_op, operation=op.mul)  # pyright: ignore[reportUnannotatedClassAttribute]
    __truediv__ = __rtruediv__ = partialmethod(_op, operation=op.truediv)  # pyright: ignore[reportUnannotatedClassAttribute]
    __gt__ = partialmethod(_op, operation=op.gt)  # pyright: ignore[reportUnannotatedClassAttribute]
    __ge__ = partialmethod(_op, operation=op.ge)  # pyright: ignore[reportUnannotatedClassAttribute]
    __lt__ = partialmethod(_op, operation=op.lt)  # pyright: ignore[reportUnannotatedClassAttribute]
    __le__ = partialmethod(_op, operation=op.le)  # pyright: ignore[reportUnannotatedClassAttribute]

    def __array__(self, dtype: npt.DTypeLike = None) -> npt.NDArray[Any]:
        if dtype is None:
            return self.stack()

        return self.stack().astype(dtype)

    @property
    def shape(self) -> tuple[int, int]:
        if self._array_numeric is not None and self._array_string is not None:
            return (self._array_numeric.shape[0], self._array_numeric.shape[1] + self._array_string.shape[1])

        if self._array_numeric is None and self._array_string is not None:
            return self._array_string.shape  # type: ignore[return-value]

        if self._array_numeric is not None and self._array_string is None:
            return self._array_numeric.shape  # type: ignore[return-value]

        return (0, 0)

    @property
    def dtype(self) -> np.dtype[Any]:
        if self._array_numeric is None and self._array_string is None:
            return np.dtype(np.float64)

        if self._array_numeric is None and self._array_string is not None:
            return self._array_string.dtype

        if self._array_numeric is not None and self._array_string is None:
            return self._array_numeric.dtype

        return np.dtype(np.object_)

    def stack(self, n: int | None = None) -> npt.NDArray[Any]:
        _subset = slice(None) if n is None else slice(0, n)

        if self._array_numeric is not None and self._array_string is not None:
            return np.hstack((self._array_numeric[_subset].astype(object), self._array_string[_subset]))

        if self._array_numeric is None and self._array_string is not None:
            return np.array(self._array_string[_subset])

        if self._array_numeric is not None and self._array_string is None:
            return np.array(self._array_numeric[_subset])

        return np.empty((0, 0))

    def sum(self, axis: int | tuple[int, ...] | None = None, out: npt.NDArray[Any] | None = None) -> Any:
        if self._array_string is not None:
            raise TypeError("Cannot apply sum with string array.")

        if self._array_numeric is None:
            return np.empty((0, 0))

        return self._array_numeric.sum(axis=axis, out=out)

    def astype(self, dtype: npt.DTypeLike) -> ArrayStack2DProxy:
        return ArrayStack2DProxy(
            np.empty(0, dtype=dtype) if self._array_numeric is None else self._array_numeric.astype(dtype),
            np.empty(0, dtype=dtype) if self._array_string is None else self._array_string.astype(dtype),
            None,
        )


@final
class EZDataFrameContainerProxy:
    __slots__: tuple[str, ...] = "_h5dfs", "_index", "_columns", "_name", "_sparse_matrices"

    def __init__(
        self,
        h5dfs: MutableMapping[str, EZDataFrame],
        name: str,
        index: RepeatingIndex | pd.Index,
        columns: RepeatingIndex | pd.Index | None = None,
    ) -> None:
        self._h5dfs = h5dfs
        self._index = index
        self._columns = columns
        self._name = name

        # FIXME : find better way
        self._sparse_matrices: set[str] = set()

    @override
    def __repr__(self) -> str:
        return f"{self._name} with keys: {', '.join(self._h5dfs.keys())}"

    def __getitem__(self, key: str) -> npt.NDArray[Any] | ss.csr_matrix:
        if str(key) in self._sparse_matrices:
            return ss.csr_matrix(self._h5dfs[str(key)].values)

        return self._h5dfs[str(key)].values

    def __setitem__(self, key: str, value: npt.NDArray[Any] | ss.spmatrix) -> None:
        if ss.issparse(value):
            self._sparse_matrices.add(str(key))
            value = np.array(value.todense())

        self._h5dfs[str(key)] = EZDataFrame(value, index=self._index, columns=self._columns)

    def __contains__(self, key: str) -> bool:
        return key in self._h5dfs.keys()

    def keys(self) -> KeysView[str]:
        return self._h5dfs.keys()
