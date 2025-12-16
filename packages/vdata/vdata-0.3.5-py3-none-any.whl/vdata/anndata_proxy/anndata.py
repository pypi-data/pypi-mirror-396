from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from os import PathLike
from typing import TYPE_CHECKING, Any, Literal, final, override

import numpy.typing as npt
import pandas as pd
from anndata import AnnData
from ezarr.dataframe import EZDataFrame
from scipy import sparse

from vdata._typing import AnyNDArrayLike
from vdata.anndata_proxy.containers import ArrayStack2DProxy, EZDataFrameContainerProxy, TemporalDataFrameContainerProxy
from vdata.anndata_proxy.dataframe import DataFrameProxy_TDF

if TYPE_CHECKING:
    from vdata.data import VData, VDataView


def skip_time_axis(slicer: Any) -> tuple[Any, ...]:
    if isinstance(slicer, tuple):
        return (slice(None),) + slicer  # pyright: ignore[reportUnknownVariableType]

    return (slice(None), slicer)


@final
class AnnDataProxy(AnnData):
    """
    Class faking to be an anndata.AnnData object but actually wrapping a VData.
    """

    __slots__: tuple[str, ...] = "_vdata", "_X", "_layers", "_obs", "_obsm", "_obsp", "_var", "_varm", "_varp", "_uns"

    def __init__(self, vdata: VData | VDataView, X: str | None = None) -> None:  # pyright: ignore[reportMissingSuperCall]
        """
        Args:
            vdata: a VData object to wrap.
            X: an optional layer name to use as X.
        """
        self._X: str | None = None if X is None else str(X)  # pyright: ignore[reportConstantRedefinition]

        if self._X is not None and self._X not in vdata.layers:
            raise ValueError(f"Could not find layer '{self._X}' in the given VData.")

        self._init_from_vdata(vdata)

    def _init_from_vdata(self, vdata: VData | VDataView) -> None:
        self._vdata = vdata
        self._layers = TemporalDataFrameContainerProxy(vdata, name="layers", columns=vdata.var.index)
        self._obs = DataFrameProxy_TDF(vdata.obs)
        self._obsm = TemporalDataFrameContainerProxy(vdata, name="obsm", columns=None)
        self._obsp = EZDataFrameContainerProxy(vdata.obsp, name="Obsp", index=vdata.obs.index, columns=vdata.obs.index)
        self._var = vdata.var
        self._varm = EZDataFrameContainerProxy(vdata.varm, name="Varm", index=vdata.var.index)
        self._varp = EZDataFrameContainerProxy(vdata.varp, name="Varp", index=vdata.var.index, columns=vdata.var.index)
        self._uns = vdata.uns

    @override
    def __repr__(self) -> str:
        return f"AnnDataProxy from {self._vdata}"

    @override
    def __sizeof__(self, *, show_stratified: bool | None = None, with_disk: bool = False) -> int:
        del show_stratified, with_disk
        raise NotImplementedError

    @override
    def __delitem__(self, index: Any) -> None:
        raise NotImplementedError

    @override
    def __getitem__(self, index: Any) -> AnnDataProxy:
        """Returns a sliced view of the object."""
        return AnnDataProxy(self._vdata[skip_time_axis(index)], X=self._X)

    @override
    def __setitem__(self, index: Any, val: int | float | npt.NDArray[Any] | sparse.spmatrix) -> None:
        raise NotImplementedError

    @property
    @override
    def n_obs(self) -> int:
        return self._vdata.n_obs_total

    @property
    @override
    def n_vars(self) -> int:
        return self._vdata.n_var

    @property
    @override
    def X(self) -> AnyNDArrayLike[Any] | None:
        if self._X is None:
            return None
        return self._vdata.layers[self._X].values

    @X.setter
    def X(self, value: Any) -> None:
        if isinstance(value, ArrayStack2DProxy):
            if value.layer_name is None:
                self._layers["X"] = value.stack()
                self._X = "X"  # pyright: ignore[reportConstantRedefinition]

        raise NotImplementedError

    @X.deleter
    def X(self) -> None:
        self._X = None  # pyright: ignore[reportConstantRedefinition]

    @property
    @override
    def layers(self) -> TemporalDataFrameContainerProxy:
        return self._layers

    @layers.setter
    def layers(self, value: Any) -> None:
        del value
        raise NotImplementedError

    @layers.deleter
    def layers(self) -> None:
        raise NotImplementedError

    @property
    @override
    def raw(self) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        raise NotImplementedError

    @raw.setter
    def raw(self, value: AnnData) -> None:  # pyright: ignore[reportPropertyTypeMismatch]
        raise NotImplementedError

    @raw.deleter
    def raw(self) -> None:
        raise NotImplementedError

    @property
    @override
    def obs(self) -> DataFrameProxy_TDF:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._obs

    @obs.setter
    def obs(self, value: pd.DataFrame) -> None:  # pyright: ignore[reportPropertyTypeMismatch]
        raise NotImplementedError

    @obs.deleter
    def obs(self) -> None:
        raise NotImplementedError

    @property
    @override
    def obs_names(self) -> pd.Index:
        """Names of observations (alias for `.obs.index`)."""
        return self.obs.index

    @obs_names.setter
    def obs_names(self, names: Sequence[str]) -> None:  # pyright: ignore[reportPropertyTypeMismatch]
        raise NotImplementedError

    @property
    @override
    def var(self) -> EZDataFrame:
        """One-dimensional annotation of variables/ features (`pd.DataFrame`)."""
        return self._var

    @var.setter
    def var(self, value: pd.DataFrame) -> None:  # pyright: ignore[reportPropertyTypeMismatch]
        raise NotImplementedError

    @var.deleter
    def var(self) -> None:
        raise NotImplementedError

    @property
    @override
    def var_names(self) -> pd.Index:
        """Names of variables (alias for `.var.index`)."""
        return self.var.index

    @var_names.setter
    def var_names(self, names: Sequence[str]) -> None:  # pyright: ignore[reportPropertyTypeMismatch]
        raise NotImplementedError

    @property
    @override
    def uns(self) -> MutableMapping[str, Any]:
        """Unstructured annotation (ordered dictionary)."""
        return self._uns

    @uns.setter
    def uns(self, value: MutableMapping[str, Any]) -> None:
        raise NotImplementedError

    @uns.deleter
    def uns(self) -> None:
        raise NotImplementedError

    @property
    @override
    def obsm(self) -> TemporalDataFrameContainerProxy:
        return self._obsm

    @obsm.setter
    def obsm(self, value: Any) -> None:
        raise NotImplementedError

    @obsm.deleter
    def obsm(self) -> None:
        raise NotImplementedError

    @property
    @override
    def varm(self) -> EZDataFrameContainerProxy:
        return self._varm

    @varm.setter
    def varm(self, value: Any) -> None:
        raise NotImplementedError

    @varm.deleter
    def varm(self) -> None:
        raise NotImplementedError

    @property
    @override
    def obsp(self) -> EZDataFrameContainerProxy:
        return self._obsp

    @obsp.setter
    def obsp(self, value: Any) -> None:
        raise NotImplementedError

    @obsp.deleter
    def obsp(self) -> None:
        raise NotImplementedError

    @property
    @override
    def varp(self) -> EZDataFrameContainerProxy:
        return self._varp

    @varp.setter
    def varp(self, value: Any) -> None:
        raise NotImplementedError

    @varp.deleter
    def varp(self) -> None:
        raise NotImplementedError

    @property
    @override
    def isbacked(self) -> bool:
        """`True` if object is backed on disk, `False` otherwise."""
        return self._vdata.is_backed

    @property
    @override
    def is_view(self) -> bool:
        """`True` if object is view of another AnnData object, `False` otherwise."""
        return self._vdata.is_view

    def as_vdata(self) -> VData | VDataView:
        return self._vdata

    @override
    def rename_categories(self, key: str, categories: Sequence[Any]) -> None:
        raise NotImplementedError

    @override
    def strings_to_categoricals(self, df: pd.DataFrame | None = None) -> None:
        raise NotImplementedError

    @override
    def _sanitize(self) -> None:
        # prevent unwanted data modification in the underlying vdata object
        return

    @override
    def _inplace_subset_var(self, index: Any) -> None:
        self._init_from_vdata(self._vdata[skip_time_axis((slice(None), index))])

    @override
    def _inplace_subset_obs(self, index: Any) -> None:
        self._init_from_vdata(self._vdata[skip_time_axis(index)])

    @override
    def copy(self, filename: PathLike[str] | str | None = None) -> AnnData:
        """Full copy, optionally on disk."""
        AnnData.copy
        raise NotImplementedError

    @override
    def write_h5ad(
        self,
        filename: PathLike[str] | str | None = None,
        *,
        convert_strings_to_categoricals: bool = True,
        compression: Literal["gzip", "lzf"] | None = None,
        compression_opts: int | Any = None,
        as_dense: Sequence[str] = (),
    ) -> None:
        raise NotImplementedError
