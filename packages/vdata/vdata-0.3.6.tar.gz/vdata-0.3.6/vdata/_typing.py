from collections.abc import Collection
from pathlib import Path
from types import EllipsisType
from typing import SupportsIndex, TypedDict

import numpy as np
import numpy.typing as npt
import zarr
from zarr.abc.store import Store
from zarr.core.buffer import Buffer
from zarr.storage import StorePath

import vdata.timepoint as tp
from vdata.array_view import NDArrayView

type IF = int | float | np.integer | np.floating
type IFS = IF | np.str_ | str
type np_IF = np.integer | np.floating
type np_IFS = np.integer | np.floating | np.str_

type AnyNDArrayLike[T: np.generic] = npt.NDArray[T] | NDArrayView[T] | zarr.Array
type AnyNDArrayLike_IF = npt.NDArray[np_IF] | NDArrayView[np_IF] | zarr.Array

type NDArrayList_IFS = npt.NDArray[np_IFS] | list[IFS]
type NDArrayLike_IFS = npt.NDArray[np_IFS] | zarr.Array
type AnyNDArrayLike_IFS = npt.NDArray[np_IFS] | NDArrayView[np_IFS] | zarr.Array

type Collection_IFS = Collection[IFS]

type Slicer = IFS | tp.TimePoint | Collection[IFS | tp.TimePoint] | range | slice | EllipsisType
type MultiSlicer = Collection[IFS | tp.TimePoint] | range | slice | EllipsisType
type PreSlicer = IFS | tp.TimePoint | Collection[IFS | bool | tp.TimePoint] | range | slice | EllipsisType
type Indexer = SupportsIndex | slice | npt.NDArray[np.int_] | npt.NDArray[np.bool_] | None

type StoreLike = Store | StorePath | Path | str | dict[str, Buffer]


class AttrDict(TypedDict):
    name: str
    timepoints_column_name: str | None
    locked_indices: bool
    locked_columns: bool
    repeating_index: bool
