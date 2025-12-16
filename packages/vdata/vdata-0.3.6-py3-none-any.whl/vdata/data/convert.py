from __future__ import annotations

import pickle
import shutil
import warnings
from collections.abc import Collection, Iterable
from pathlib import Path
from typing import Any, Literal, overload

import ch5mpy as ch
import ezarr as ez
import numpy as np
import numpy.typing as npt
from anndata import AnnData
from ezarr.dataframe import EZDataFrame
from ezarr.names import Attribute, EZType
from tqdm.auto import tqdm
from zarr.codecs.numcodecs import LZ4
from zarr.errors import UnstableSpecificationWarning, ZarrUserWarning

import vdata
import vdata.timepoint as tp
from vdata._typing import IFS
from vdata.array_view import NDArrayView
from vdata.data.name import WRITE_PROTOCOL_VERSION
from vdata.IO.logger import generalLogger
from vdata.tdf import TemporalDataFrame
from vdata.utils import repr_array


class NoBar:
    def update(self) -> None:
        pass

    def close(self) -> None:
        pass


@overload
def convert_vdata_to_anndata(
    data: vdata.VData,
    into_one: Literal[True] = True,
    timepoints_list: str | tp.TimePoint | Collection[str | tp.TimePoint] | None = None,
    with_timepoints_column: bool = True,
    layer_as_X: str | None = None,
    layers_to_export: list[str] | None = None,
) -> AnnData: ...
@overload
def convert_vdata_to_anndata(
    data: vdata.VData,
    into_one: Literal[False],
    timepoints_list: str | tp.TimePoint | Collection[str | tp.TimePoint] | None = None,
    with_timepoints_column: bool = True,
    layer_as_X: str | None = None,
    layers_to_export: list[str] | None = None,
) -> list[AnnData]: ...
def convert_vdata_to_anndata(
    data: vdata.VData,
    into_one: bool = True,
    timepoints_list: str | tp.TimePoint | Collection[str | tp.TimePoint] | None = None,
    with_timepoints_column: bool = True,
    layer_as_X: str | None = None,
    layers_to_export: list[str] | None = None,
) -> AnnData | list[AnnData]:
    """
    Convert a VData object to an AnnData object.

    Args:
        timepoints_list: a list of time points for which to extract data to build the AnnData. If set to
            None, all timepoints are selected.
        into_one: Build one AnnData, concatenating the data for multiple time points (True), or build one
            AnnData for each time point (False) ?
        with_timepoints_column: store time points data in the obs DataFrame. This is only used when
            concatenating the data into a single AnnData (i.e. into_one=True).
        layer_as_X: name of the layer to use as the X matrix. By default, the first layer is used.
        layers_to_export: if None export all layers

    Returns:
        An AnnData object with data for selected time points.
    """
    # TODO : obsp is not passed to AnnData

    generalLogger.debug(
        "\u23be VData conversion to AnnData : begin ---------------------------------------------------------- "
    )

    if timepoints_list is None:
        _timepoints_list: tp.TimePointNArray | NDArrayView[tp.TimePoint] = data.timepoints_values

    else:
        _timepoints_list = tp.as_timepointarray(timepoints_list)
        _timepoints_list = tp.atleast_1d(_timepoints_list[np.where(np.isin(_timepoints_list, data.timepoints_values))])

    generalLogger.debug(f"Selected time points are : {repr_array(_timepoints_list)}")

    if into_one:
        return _convert_vdata_into_one_anndata(
            data, with_timepoints_column, _timepoints_list, layer_as_X, layers_to_export
        )

    return _convert_vdata_into_many_anndatas(data, _timepoints_list, layer_as_X)


def _convert_vdata_into_one_anndata(
    data: vdata.VData,
    with_timepoints_column: bool,
    timepoints_list: tp.TimePointNArray | NDArrayView[tp.TimePoint],
    layer_as_X: str | None,
    layers_to_export: Iterable[str] | None,
) -> AnnData:
    generalLogger.debug("Convert to one AnnData object.")

    tp_col_name = data.obs.get_timepoints_column_name() if with_timepoints_column else None

    view = data[timepoints_list]
    if layer_as_X is None:
        layer_as_X = list(view.layers.keys())[0]

    elif layer_as_X not in view.layers.keys():
        raise ValueError(f"Layer '{layer_as_X}' was not found.")

    X = view.layers[layer_as_X].to_pandas()
    X.index = X.index.astype(str)
    X.columns = X.columns.astype(str)

    layers_to_export_ = view.layers.keys() if layers_to_export is None else layers_to_export

    anndata = AnnData(
        X=X,
        layers={key: np.array(view.layers[key]) for key in layers_to_export_},
        obs=view.obs.to_pandas(with_timepoints=tp_col_name, str_index=True),
        obsm={str(key): np.array(arr) for key, arr in view.obsm.items()},
        obsp={str(key): np.array(arr.copy()) for key, arr in view.obsp.items()},
        var=view.var.copy(),
        varm=view.varm.dict_copy(str_columns=True),
        varp=view.varp.dict_copy(str_columns=True),
        uns=view.uns.copy(),
    )

    generalLogger.debug(
        "\u23bf VData conversion to AnnData : end ---------------------------------------------------------- "
    )

    return anndata


def _convert_vdata_into_many_anndatas(
    data: vdata.VData,
    timepoints_list: tp.TimePointNArray | NDArrayView[tp.TimePoint],
    layer_as_X: str | None,
) -> list[AnnData]:
    generalLogger.debug("Convert to many AnnData objects.")

    result = []
    for time_point in timepoints_list:
        view = data[time_point]

        if layer_as_X is None:
            layer_as_X = list(view.layers.keys())[0]

        elif layer_as_X not in view.layers.keys():
            raise ValueError(f"Layer '{layer_as_X}' was not found.")

        X = view.layers[layer_as_X].to_pandas()
        X.index = X.index.astype(str)
        X.columns = X.columns.astype(str)

        result.append(
            AnnData(
                X=X,
                layers={key: np.array(layer) for key, layer in view.layers.items()},
                obs=view.obs.to_pandas(str_index=True),
                obsm={str(key): np.array(arr) for key, arr in view.obsm.items()},
                var=view.var.copy(),
                varm=view.varm.dict_copy(),
                varp=view.varp.dict_copy(),
                uns=view.uns,
            )
        )

    generalLogger.debug(
        "\u23bf VData conversion to AnnData : end ---------------------------------------------------------- "
    )

    return result


def as_nparray(obj: ch.H5Array[Any] | ch.H5Dict[Any]) -> npt.NDArray[Any]:
    if isinstance(obj, ch.H5Array):
        return obj.copy()

    if "categories" not in obj:
        raise ValueError(f"Cannot convert '{obj}' to numpy.array")

    arr = obj["categories"][obj["codes"]]

    if arr.dtype == object:
        arr = arr.astype(str)

    return arr


def convert_to_TDF(
    obj: ch.H5Dict[Any],
    data: ez.EZDict[Any],
    layer_name: str,
    timepoints: tp.TimePointIndex,
    index: ch.H5Array[Any],
    columns: ch.H5Array[Any],
    sorting_indices: npt.NDArray[np.integer],
    progressBar: tqdm[Any] | NoBar,
) -> None:
    if obj.attributes.get("encoding-type", "") == "csr_matrix":
        raise NotImplementedError
        # data[layer_name].attributes.set(
        #     __h5_type__="object",
        #     __h5_class__=np.void(pickle.dumps(csp.H5_csr_array, protocol=pickle.HIGHEST_PROTOCOL)),
        #     _shape=data[layer_name].attributes["shape"],
        # )

    assert len(index) == obj.shape[0]

    data.attrs.put(
        {
            "name": layer_name,
            "timepoints_column_name": None,
            "repeating_index": False,
            "locked_indices": False,
            "locked_columns": False,
            Attribute.EZType: EZType.Object,
        }
    )

    with warnings.catch_warnings(action="ignore", category=ZarrUserWarning):
        compressors = LZ4()

    with data.parameters(compressors):
        data["timepoints_index"] = timepoints
        data["index"] = index[sorting_indices]
        data["columns_numerical"] = columns
        data["columns_string"] = np.empty(shape=(0,), dtype=str)
        data["array_numerical"] = obj[sorting_indices]  # pyright: ignore[reportArgumentType]
        data["array_string"] = np.empty(shape=(obj.shape[0], 0), dtype=str)

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            data.create_array(
                Attribute.EZClass,
                data=np.void(pickle.dumps(vdata.TemporalDataFrame, protocol=pickle.HIGHEST_PROTOCOL)),  # pyright: ignore[reportArgumentType]
                overwrite=True,
            )

    progressBar.update()


def _convert_anndata_to_vdata(
    data: ch.H5Dict[Any],
    z_data: ez.EZDict[Any],
    timepoint: IFS | tp.TimePoint,
    timepoints_column_name: str | None,
    drop_X: bool,
    progressBar: tqdm[Any] | NoBar,
) -> None:
    r"""
    Convert an anndata h5 file into a valid vdata h5 file.
    /!\ WARNING : if done inplace, you won't be able to open the file as an anndata anymore !

    Args:
        - path: path to the anndata h5 file to convert.
        - timepoint: a unique timepoint to set for the data in the anndata.
        - timepoints_column_name: the name of the column in anndata's obs to use as indicator of time point for the data.
        - drop_X: do not preserve the 'X' dataset ? (default: False)
    """
    z_data.attrs["__vdata_write_version__"] = WRITE_PROTOCOL_VERSION

    # timepoints --------------------------------------------------------------
    timepoint = tp.TimePoint(timepoint)

    if timepoints_column_name is not None:
        if timepoints_column_name not in data["obs"]:
            raise ValueError(f"Could not find column '{timepoints_column_name}' in obs columns.")

        timepoints_list = tp.as_timepointarray(as_nparray(data["obs"][timepoints_column_name]))

    else:
        timepoints_list = tp.TimePointNArray(
            np.ones(data["obs"][next(iter(data["obs"]))].shape[0]) * timepoint.value, unit=timepoint.unit
        )

    _unique_tps = np.unique(timepoints_list, equal_nan=False)
    z_data["timepoints"] = EZDataFrame(
        {"value": _unique_tps, "unit": np.repeat(timepoints_list.unit, len(_unique_tps))}
    )
    progressBar.update()

    # obs ---------------------------------------------------------------------
    # TODO: maybe better to convert inplace without creating a whole TDF
    _obs_index = data["obs"]["_index"].astype(str)
    obs_data: dict[str, npt.NDArray[Any]] = {
        k: as_nparray(v) for k, v in data["obs"].items() if k not in (timepoints_column_name, "_index")
    }

    z_data["obs"] = TemporalDataFrame(
        obs_data, index=_obs_index, timepoints=timepoints_list, lock=(True, False), name="obs"
    )

    progressBar.update()

    # var ---------------------------------------------------------------------
    var_data = data["var"].copy()

    if "_index" in data["var"]:
        _var_index = data["var"]["_index"].astype(str)

        del var_data["_index"]

    elif "_index" in data["var"].attributes:
        _var_index = data["var"][data["var"].attributes["_index"]]

    else:
        raise ValueError("Could not find index for var dataframe")

    z_data["var"] = EZDataFrame(var_data, index=_var_index)

    progressBar.update()

    # layers ------------------------------------------------------------------
    sorting_indices = np.argsort(timepoints_list, kind="stable").astype(int)
    z_data["layers"] = {}

    if not drop_X:
        z_data["layers"]["X"] = {}
        convert_to_TDF(
            data["X"],
            z_data["layers"]["X"],
            "X",
            (z_data @ "obs")["timepoints_index"],  # pyright: ignore[reportArgumentType]
            _obs_index,
            _var_index,
            sorting_indices,
            progressBar,
        )

    for layer_name in data["layers"]:
        z_data["layers"][layer_name] = {}
        convert_to_TDF(
            data["layers"][layer_name],
            z_data["layers"][layer_name],
            layer_name,
            (z_data @ "obs")["timepoints_index"],  # pyright: ignore[reportArgumentType]
            _obs_index,
            _var_index,
            sorting_indices,
            progressBar,
        )

    # obsm --------------------------------------------------------------------
    z_data["obsp"] = {}
    for array_name, array_data in data["obsm"].items():
        data["obsm"][array_name] = TemporalDataFrame(
            array_data, index=_obs_index, timepoints=timepoints_list, lock=(True, False), name=array_name
        )

        progressBar.update()

    # obsp --------------------------------------------------------------------
    z_data["obsp"] = {}
    for array_name, array_data in data["obsp"].items():
        data["obsp"][array_name] = EZDataFrame(array_data, index=_obs_index, columns=_obs_index)

        progressBar.update()

    # varm --------------------------------------------------------------------
    z_data["varm"] = {}
    for array_name, array_data in data["varm"].items():
        data["varm"][array_name] = EZDataFrame(array_data, index=_var_index)

        progressBar.update()

    # varp --------------------------------------------------------------------
    z_data["varp"] = {}
    for array_name, array_data in data["varp"].items():
        data["varp"][array_name] = EZDataFrame(array_data, index=_var_index, columns=_var_index)

        progressBar.update()

    # uns ---------------------------------------------------------------------
    z_data["uns"] = {}


def convert_anndata_to_vdata(
    path: Path | str,
    timepoint: IFS | tp.TimePoint = tp.TimePoint("0h"),  # pyright: ignore[reportCallInDefaultInitializer]
    timepoints_column_name: str | None = None,
    drop_X: bool = False,
    verbose: bool = True,
) -> ez.EZDict[Any]:
    r"""
    Convert an anndata h5 file into a valid vdata h5 file.
    /!\ WARNING : if done inplace, you won't be able to open the file as an anndata anymore !

    Args:
        path: path to the anndata h5 file to convert.
        timepoint: a unique timepoint to set for the data in the anndata.
        timepoints_column_name: the name of the column in anndata's obs to use as indicator of time point for the data.
        drop_X: do not preserve the 'X' dataset ? (default: False)
    """
    path = Path(path)
    data = ch.H5Dict.read(path, mode=ch.H5Mode.READ_WRITE)
    z_data = ez.EZDict[Any].open(path.with_suffix(".vd"))

    if verbose:
        nb_items_to_write = (
            3
            + len(data["layers"])
            + len(data["obsm"])
            + len(data["obsp"])
            + len(data["varm"])
            + len(data["varp"])
            + int(not drop_X)
        )
        progressBar = tqdm(total=nb_items_to_write, desc="Converting anndata to VData", unit="object")

    else:
        progressBar = NoBar()

    try:
        _convert_anndata_to_vdata(data, z_data, timepoint, timepoints_column_name, drop_X, progressBar=progressBar)

    except Exception as e:
        shutil.rmtree(path.with_suffix(".vd"))

        raise e

    finally:
        progressBar.close()

    return z_data
