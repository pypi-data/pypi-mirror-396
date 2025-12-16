from __future__ import annotations

from typing import Any, Hashable, cast, override

import numpy as np
import numpy.typing as npt
import pandas as pd
from pandas._libs.internals import BlockValuesRefs
from pandas.core.arrays import ExtensionArray


class RepeatingIndex(pd.Index):
    """An Index that may repeat its values mutliple times."""

    _metadata: list[str] = ["repeats"]
    repeats: int  # pyright: ignore[reportUninitializedInstanceVariable]

    def __new__(
        cls,
        data: Any,
        repeats: int = 1,
    ) -> RepeatingIndex:
        data = np.tile(np.array(data), repeats)
        return cast(RepeatingIndex, cls._simple_new(data, None, repeats=repeats))

    @classmethod
    @override
    def _simple_new(
        cls: type[RepeatingIndex],
        values: npt.NDArray[Any] | ExtensionArray,
        name: Hashable | None = None,
        refs: BlockValuesRefs | None = None,
        repeats: int | None = None,
    ) -> RepeatingIndex | pd.Index:
        if repeats is None:
            return pd.Index._simple_new(values, name, refs)

        assert isinstance(values, cls._data_cls), type(values)

        if repeats == 1 and len(values) != len(np.unique(values)):  # pyright: ignore[reportCallIssue, reportArgumentType]
            raise ValueError("Index values must be all unique if not repeating.")

        result = object.__new__(cls)
        result._data = values
        result._name = name
        result._cache = {}
        result._reset_identity()
        if refs is not None:
            result._references = refs
        else:
            result._references = BlockValuesRefs()
        result._references.add_index_reference(result)

        result.repeats = repeats

        return result

    @override
    def __hash__(self) -> int:  # pyright: ignore[reportIncompatibleVariableOverride]
        return hash(self.values.data.tobytes()) + int(self.is_repeating)  # pyright: ignore[reportAttributeAccessIssue]

    @property
    @override
    def _constructor(self) -> type[pd.Index]:
        return pd.Index

    @property
    def is_repeating(self) -> bool:
        return self.repeats > 1

    @override
    def _format_attrs(self) -> list[tuple[str, str | int | bool | None]]:
        attrs = super()._format_attrs()
        attrs.append(("repeating", self.is_repeating))
        return attrs
