from __future__ import annotations

from collections.abc import Collection, Iterable
from typing import Any, ClassVar, Literal, NoReturn, Self, override

import ch5mpy.indexing as ci
import ezarr as ez
import numpy.typing as npt
import zarr

from vdata._typing import IFS, Indexer, np_IFS
from vdata.array_view import ArrayGetter, NDArrayView
from vdata.tdf.base import TemporalDataFrameBase
from vdata.tdf.dataframe import TemporalDataFrame
from vdata.tdf.index import RepeatingIndex


def _as_view(
    container: TemporalDataFrameBase,
    name: str,
    index: Indexer | tuple[Indexer, ...],
    exposed_attributes: Iterable[str] = (),
) -> zarr.Array | NDArrayView[Any]:
    # if isinstance(getattr(container, name), zarr.Array):
    #     return NDArrayView(ArrayGetter(container, name), index, exposed_attributes)
    #     arr = getattr(container, name)[index]
    #     assert isinstance(arr, zarr.Array)
    #     return arr
    #
    return NDArrayView(ArrayGetter(container, name), index, exposed_attributes)


class TemporalDataFrameView(TemporalDataFrameBase):
    """
    A view of a TemporalDataFrame object.
    """

    __ez_class__: ClassVar[type] = TemporalDataFrame

    _attributes: set[str] = TemporalDataFrameBase._attributes.union(
        {"_parent", "_numerical_selection", "_string_selection", "_inverted"}
    )

    def __init__(
        self,
        parent: TemporalDataFrameBase,
        numerical_selection: ci.Selection,
        string_selection: ci.Selection,
        *,
        inverted: bool = False,
    ):
        if isinstance(parent, TemporalDataFrameView):
            numerical_selection = numerical_selection.cast_on(parent._numerical_selection)
            string_selection = string_selection.cast_on(parent._string_selection)

            root: TemporalDataFrame = parent.parent

        else:
            assert isinstance(parent, TemporalDataFrame)
            root = parent

        super().__init__(
            index=_as_view(root, "_index", ci.get_indexer(numerical_selection[0], enforce_1d=True)),
            timepoints_index=root.timepoints_index[numerical_selection[0]],
            array_numerical=_as_view(root, "values_num", numerical_selection.get_indexers()),
            array_string=_as_view(root, "values_str", string_selection.get_indexers()),
            columns_numerical=_as_view(root, "columns_num", ci.get_indexer(numerical_selection[1], enforce_1d=True)),
            columns_string=_as_view(root, "columns_str", ci.get_indexer(string_selection[1], enforce_1d=True)),
            attr_dict=root._attr_dict,
            data=root.data,
        )

        self._parent: TemporalDataFrame = root
        self._numerical_selection: ci.Selection = numerical_selection
        self._string_selection: ci.Selection = string_selection
        self._inverted: bool = inverted

    @classmethod
    @override
    def __ez_read__(cls, values: ez.EZDict[Any]) -> Self:
        raise TypeError("Cannot read a TemporalDataFrame view directly, read as a TemporalDataFrame instead.")

    @override
    def __delattr__(self, _column_name: str) -> NoReturn:
        raise TypeError("Cannot delete columns from a view.")

    @override
    def __invert__(self) -> TemporalDataFrameView:
        """
        Invert the getitem selection behavior : all elements NOT present in the slicers will be selected.
        """
        return type(self)(
            parent=self._parent,
            numerical_selection=self._numerical_selection,
            string_selection=self._string_selection,
            inverted=not self._inverted,
        )

    @property
    @override
    def full_name(self) -> str:
        """
        Get the full name.
        """
        parts: list[str] = []
        if self.empty:
            parts.append("empty")

        if self.is_inverted:
            parts.append("inverted")

        parent_full_name = self._parent.full_name
        if not parent_full_name.startswith("TemporalDataFrame"):
            parent_full_name = parent_full_name[0].lower() + parent_full_name[1:]

        parts += ["view of", parent_full_name]

        parts[0] = parts[0].capitalize()

        return " ".join(parts)

    @property
    def parent(self) -> TemporalDataFrame:
        """Get the parent TemporalDataFrame of this view."""
        return self._parent

    @property
    @override
    def is_view(self) -> Literal[True]:
        """
        Is this a view on a TemporalDataFrame ?
        """
        return True

    @property
    @override
    def is_inverted(self) -> bool:
        """
        Whether this view of a TemporalDataFrame is inverted or not.
        """
        return self._inverted

    @override
    def _append_column(self, column_name: IFS, values: npt.NDArray[np_IFS]) -> None:
        raise NotImplementedError

    @override
    def lock_indices(self) -> None:
        """Lock the "index" axis to prevent modifications."""
        self._parent.lock_indices()

    @override
    def unlock_indices(self) -> None:
        """Unlock the "index" axis to allow modifications."""
        self._parent.unlock_indices()

    @override
    def lock_columns(self) -> None:
        """Lock the "columns" axis to prevent modifications."""
        self._parent.lock_columns()

    @override
    def unlock_columns(self) -> None:
        """Unlock the "columns" axis to allow modifications."""
        self._parent.unlock_columns()

    @override
    def set_index(
        self,
        values: Collection[IFS] | RepeatingIndex,
        *,
        force: bool = False,
    ) -> None:
        """Set new index values."""
        raise NotImplementedError

    @override
    def reindex(self, order: npt.NDArray[np_IFS] | RepeatingIndex) -> None:
        """Re-order rows in this TemporalDataFrame so that their index matches the new given order."""
        raise NotImplementedError

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
        raise NotImplementedError
