from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection, ItemsView, Iterator, KeysView, MutableMapping, ValuesView
from pathlib import Path
from typing import override

import numpy as np
import pandas as pd
from ezarr.dataframe import EZDataFrame

import vdata
from vdata._typing import IFS
from vdata.data.arrays.lazy import LazyLoc
from vdata.IO import generalLogger
from vdata.tdf import RepeatingIndex, TemporalDataFrame, TemporalDataFrameView
from vdata.tdf.base import TemporalDataFrameBase
from vdata.utils import first_in


# Base Containers -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
class ArrayContainerMixin[
    D: TemporalDataFrameBase | EZDataFrame | LazyLoc,
    D_copy: TemporalDataFrame | pd.DataFrame,
](MutableMapping[str, D], ABC):
    @property
    def empty(self) -> bool:
        """Whether this view is empty or not."""
        return all([v.empty for v in self.values()])

    @property
    @abstractmethod
    def name(self) -> str: ...

    @override
    @abstractmethod
    def keys(self) -> KeysView[str]:
        """
        KeysView of keys for getting the data items in this ArrayContainer.

        Returns:
            KeysView of this ArrayContainer.
        """

    @override
    @abstractmethod
    def values(self) -> ValuesView[D]:
        """
        ValuesView of data items in this ArrayContainer.

        Returns:
            ValuesView of this ArrayContainer.
        """

    @override
    @abstractmethod
    def items(self) -> ItemsView[str, D]:
        """
        ItemsView of pairs of keys and data items in this ArrayContainer.

        Returns:
            ItemsView of this ArrayContainer.
        """

    def dict_copy(self, deep: bool = True, str_columns: bool = False) -> dict[str, D_copy]:
        """Dictionary of keys and data items in this view."""
        d: dict[str, D_copy] = {}
        for k, v in self.items():
            v_copy = v.copy(deep=deep)

            if str_columns:
                v_copy.columns = v_copy.columns.astype(str)

            d[k] = v_copy

        return d

    def to_csv(
        self,
        directory: Path,
        sep: str = ",",
        na_rep: str = "",
        index: bool = True,
        header: bool = True,
        spacer: str = "",
    ) -> None:
        """
        Save this view in CSV file format.

        Args:
            directory: path to a directory for saving the Array
            sep: delimiter character
            na_rep: string to replace NAs
            index: write row names ?
            header: Write col names ?
            spacer: for logging purposes, the recursion depth of calls to a read_h5 function.
        """
        path = Path(directory) / self.name
        path.mkdir(parents=True, exist_ok=True)

        for item_name, item in self.items():
            generalLogger.info(f"{spacer}Saving {item_name}")
            item.to_csv(f"{path / item_name}.csv", sep, na_rep, index=index, header=header)


class VBaseArrayContainer[
    D: TemporalDataFrameBase | EZDataFrame,
    D_copy: TemporalDataFrame | pd.DataFrame,
](ArrayContainerMixin[D, D_copy], ABC):
    """
    Base abstract class for ArrayContainers linked to a VData object (obsm, obsp, varm, varp, layers).
    All Arrays have a '_parent' attribute for linking them to a VData and a '_data' dictionary
    attribute for storing 2D/3D arrays.
    """

    __slots__: tuple[str, ...] = "_vdata", "_data"

    def __init__(self, *, data: MutableMapping[str, D], vdata: vdata.VData):
        """
        Args:
            vdata: the parent VData object this ArrayContainer is linked to.
            data: a dictionary of data items (DataFrames, TemporalDataFrames or dictionaries of DataFrames)
                to store in this ArrayContainer.
        """
        generalLogger.debug(f"== Creating {type(self).__name__}. ==========================")

        self._vdata: vdata.VData = vdata
        self._data: MutableMapping[str, D] = self._check_init_data(data)

    @abstractmethod
    def _check_init_data(self, data: MutableMapping[str, D]) -> MutableMapping[str, D]:
        """
        Function for checking, at ArrayContainer creation, that the supplied data has the correct format.

        Args:
            data: optional dictionary of data items.
        Returns:
            The data, if correct.
        """
        pass

    @override
    def __repr__(self) -> str:
        """
        Get a string representation of this ArrayContainer.
        :return: a string representation of this ArrayContainer.
        """
        if not len(self):
            return f"Empty {type(self).__name__}."

        return f"{type(self).__name__} with keys: {', '.join(map(repr, self.keys()))}."

    @override
    def __getitem__(self, item: str) -> D:
        """
        Get a specific data item stored in this ArrayContainer.

        Args:
            item: key in _data linked to a data item.

        Returns:
            Data item stored in _data under the given key.
        """
        if item not in self.keys():
            raise AttributeError(f"This {type(self).__name__} has no attribute '{item}'")

        return self.data[item]  # type: ignore[return-value]

    @override
    @abstractmethod
    def __setitem__(self, key: str, value: D) -> None:
        """
        Set a specific data item in _data. The given data item must have the correct shape.

        Args:
            key: key for storing a data item in this ArrayContainer.
            value: a data item to store.
        """
        pass

    @override
    def __delitem__(self, key: str) -> None:
        """
        Delete a specific data item stored in this ArrayContainer.
        """
        del self.data[key]

    @override
    def __len__(self) -> int:
        """
        Length of this ArrayContainer : the number of data items in _data.
        :return: number of data items in _data.
        """
        return len(self._data.keys())

    @override
    def __iter__(self) -> Iterator[str]:
        """
        Iterate on this ArrayContainer's keys.
        :return: an iterator over this ArrayContainer's keys.
        """
        return iter(self.keys())

    @property
    @override
    def name(self) -> str:
        return type(self).__name__[1:-14].lower()

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
        The shape of this ArrayContainer is computed from the shape of the Arrays it contains.
        See __len__ for getting the number of Arrays it contains.

        Returns:
            The shape of this ArrayContainer.
        """
        pass

    @property
    def data(self) -> MutableMapping[str, D]:
        """
        Data of this ArrayContainer.

        Returns:
            The data of this ArrayContainer.
        """
        return self._data

    @override
    def keys(self) -> KeysView[str]:
        """
        KeysView of keys for getting the data items in this ArrayContainer.

        Returns:
            KeysView of this ArrayContainer.
        """
        return self._data.keys()

    @override
    def values(self) -> ValuesView[D]:
        """
        ValuesView of data items in this ArrayContainer.

        Returns:
            ValuesView of this ArrayContainer.
        """
        return self._data.values()  # type: ignore[return-value]

    @override
    def items(self) -> ItemsView[str, D]:
        """
        ItemsView of pairs of keys and data items in this ArrayContainer.

        Returns:
            ItemsView of this ArrayContainer.
        """
        return self._data.items()  # type: ignore[return-value]


# 3D Containers -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -
class VTDFArrayContainer(VBaseArrayContainer[TemporalDataFrame | TemporalDataFrameView, TemporalDataFrame], ABC):
    """
    Base abstract class for ArrayContainers linked to a VData object that contain TemporalDataFrames (obsm and layers).
    It is based on VBaseArrayContainer and defines some functions shared by obsm and layers.
    """

    def __init__(self, *, data: MutableMapping[str, TemporalDataFrame | TemporalDataFrameView], vdata: vdata.VData):
        """
        Args:
            parent: the parent VData object this ArrayContainer is linked to.
            data: a dictionary of TemporalDataFrames in this ArrayContainer.
        """
        super().__init__(data=data, vdata=vdata)

    @override
    def __setitem__(self, key: str, value: TemporalDataFrame | TemporalDataFrameView) -> None:
        """
        Set a specific TemporalDataFrame in _data. The given TemporalDataFrame must have the correct shape.

        Args:
            key: key for storing a TemporalDataFrame in this VObsmArrayContainer.
            value: a TemporalDataFrame to store.
        """
        if not np.array_equal(self._vdata.timepoints_values, value.timepoints):
            raise ValueError("Time-points do not match.")

        if not np.array_equal(self._vdata.obs.index, value.index):
            raise ValueError("Index does not match.")

        self.data[key] = value

    @property
    @override
    def shape(self) -> tuple[int, int, list[int], list[int]]:
        """
        The shape of this ArrayContainer is computed from the shape of the TemporalDataFrames it contains.
        See __len__ for getting the number of TemporalDataFrames it contains.

        Returns:
            (<nb TDFs>, <nb time-points>, <nb obs>, <nb vars>)
        """
        if not len(self):
            return 0, 0, [], []

        _shape_TDF = first_in(self.data).shape
        return len(self.data), _shape_TDF[0], _shape_TDF[1], [d.shape[2] for d in self.values()]

    def set_index(self, values: Collection[IFS] | RepeatingIndex) -> None:
        """Set a new index for rows."""
        for layer in self.values():
            layer.set_index(values, force=True)

    def set_columns(self, values: Collection[IFS]) -> None:
        """Set a new index for columns."""
        for layer in self.values():
            layer.unlock_columns()
            layer.columns = np.array(values)
            layer.lock_columns()
