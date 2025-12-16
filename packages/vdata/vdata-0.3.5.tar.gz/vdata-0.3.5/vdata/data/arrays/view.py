from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import ItemsView, Iterator, KeysView, MutableMapping, ValuesView
from typing import override

import numpy as np
import numpy.typing as npt
import pandas as pd
from ezarr.dataframe import EZDataFrame

import vdata.timepoint as tp
from vdata._typing import np_IFS
from vdata.array_view import NDArrayView
from vdata.data.arrays.base import ArrayContainerMixin, VBaseArrayContainer
from vdata.data.hash import VDataHash
from vdata.IO import generalLogger
from vdata.tdf import RepeatingIndex, TemporalDataFrame
from vdata.tdf.base import TemporalDataFrameBase
from vdata.utils import first_in


class VBaseArrayContainerView[
    D: TemporalDataFrameBase | EZDataFrame,
    D_copy: TemporalDataFrame | pd.DataFrame,
](ArrayContainerMixin[D, D_copy], ABC):
    """
    A base abstract class for views of VBaseArrayContainers.
    This class is used to create views on array containers.
    """

    def __init__(
        self,
        data: MutableMapping[str, D],
        array_container: VBaseArrayContainer[D, D_copy],
        hash: VDataHash,
    ):
        """
        Args:
            array_container: a VBaseArrayContainer object to build a view on.
        """
        generalLogger.debug(f"== Creating {type(self).__name__}. ================================")

        self._data: MutableMapping[str, D] = data
        self._array_container: VBaseArrayContainer[D, D_copy] = array_container
        self._hash: VDataHash = hash

    @override
    def __repr__(self) -> str:
        """Description for this view  to print."""
        return f"View of {self._array_container}"

    @override
    def __getitem__(self, key: str) -> D:
        """Get a specific data item stored in this view."""
        return self.data[key]

    @abstractmethod
    @override
    def __setitem__(self, key: str, value: D) -> None:
        """Set a specific data item in this view. The given data item must have the correct shape."""

    @override
    def __delitem__(self, key: str) -> None:
        del key
        raise TypeError("Cannot delete data from view.")

    @override
    def __len__(self) -> int:
        """Length of this view : the number of data items in the VBaseArrayContainer."""
        return len(self.keys())

    @override
    def __iter__(self) -> Iterator[str]:
        """Iterate on this view's keys."""
        return iter(self.keys())

    @property
    @override
    def name(self) -> str:
        """Name for this view."""
        return f"{self._array_container.name}_view"

    @property
    @abstractmethod
    def shape(
        self,
    ) -> (
        tuple[int, int, int]
        | tuple[int, int, list[int]]
        | tuple[int, int, list[int], int]
        | tuple[int, int, list[int], list[int]]
    ):
        """
        The shape of this view is computed from the shape of the Arrays it contains.
        See __len__ for getting the number of Arrays it contains.
        """
        pass

    @property
    def data(self) -> MutableMapping[str, D]:
        """Data of this view."""
        try:
            self._hash.assert_unchanged()
        except AssertionError:
            raise ValueError("View no longer valid since parent's VData has changed.")

        return self._data

    @override
    def keys(self) -> KeysView[str]:
        """KeysView of keys for getting the data items in this view."""
        return self.data.keys()

    @override
    def values(self) -> ValuesView[D]:
        """ValuesView of data items in this view."""
        return self.data.values()

    @override
    def items(self) -> ItemsView[str, D]:
        """ItemsView of pairs of keys and data items in this view."""
        return self.data.items()


class VTDFArrayContainerView(VBaseArrayContainerView[TemporalDataFrameBase, TemporalDataFrame]):
    """
    Base abstract class for views of ArrayContainers that contain TemporalDataFrames (layers and obsm).
    It is based on VBaseArrayContainer.
    """

    def __init__(
        self,
        array_container: VBaseArrayContainer[TemporalDataFrameBase, TemporalDataFrame],
        timepoints_slicer: tp.TimePointNArray | NDArrayView[tp.TimePoint],
        obs_slicer: npt.NDArray[np_IFS],
        var_slicer: npt.NDArray[np_IFS] | slice,
    ):
        """
        Args:
            array_container: a VBaseArrayContainer object to build a view on.
            timepoints_slicer: the list of time points to view.
            obs_slicer: the list of observations to view.
            var_slicer: the list of variables to view.
        """
        super().__init__(
            data={key: tdf[timepoints_slicer, obs_slicer, var_slicer] for key, tdf in array_container.items()},
            array_container=array_container,
            hash=VDataHash(array_container._vdata, timepoints=True, obs=True, var=True),  # pyright: ignore[reportPrivateUsage]
        )

    @override
    def __setitem__(self, key: str, value: TemporalDataFrameBase) -> None:
        """Set a specific data item in this view. The given data item must have the correct shape."""
        self.data[key] = value

    @property
    @override
    def shape(self) -> tuple[int, int, list[int], int]:
        """
        The shape of this view is computed from the shape of the Arrays it contains.
        See __len__ for getting the number of Arrays it contains.
        """
        if not len(self):
            return 0, 0, [], 0

        return len(self), *first_in(self.data).shape

    def set_index(self, values: npt.NDArray[np_IFS] | RepeatingIndex) -> None:
        """Set a new index for rows."""
        for layer in self.values():
            layer.unlock_indices()
            layer.set_index(values)
            layer.lock_indices()

    def set_columns(self, values: npt.NDArray[np_IFS]) -> None:
        """Set a new index for columns."""
        for layer in self.values():
            layer.unlock_columns()
            layer.columns = np.array(values)
            layer.lock_columns()
