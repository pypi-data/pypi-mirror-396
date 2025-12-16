from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

import ezarr as ez
from tqdm.auto import tqdm
from zarr.codecs.numcodecs import LZ4
from zarr.errors import ZarrUserWarning

from vdata._typing import StoreLike
from vdata.data.name import WRITE_PROTOCOL_VERSION
from vdata.IO.logger import generalLogger
from vdata.utils import spacer

if TYPE_CHECKING:
    from vdata.data.vdata import VData
    from vdata.data.view import VDataView


def write_vdata_in_ezdict(data: VData | VDataView, values: ez.EZDict[Any], verbose: bool = True) -> None:
    generalLogger.debug("⎾ VData write to zarr : start ----------------------------------------------------- ")

    nb_items_to_write = (
        len(data.layers) + len(data.obsm) + len(data.obsp) + len(data.varm) + len(data.varp) + len(data.uns) + 3
    )
    progressBar = tqdm(total=nb_items_to_write, desc=f"writing VData {data.name}", unit="object") if verbose else None

    values.attrs.put({"name": data.name, "__vdata_write_version__": WRITE_PROTOCOL_VERSION})
    values.update(layers={}, obsm={}, obsp={}, varm={}, varp={}, uns={})

    with warnings.catch_warnings(action="ignore", category=ZarrUserWarning):
        compressors = LZ4()

    with values.parameters(compressors=compressors):
        for name, obj in [("obs", data.obs), ("var", data.var), ("timepoints", data.timepoints)]:
            generalLogger.debug(f"  ↳ writing {name}")
            values[name] = obj

            if progressBar:
                progressBar.update()

        for base, container in (
            ("layers", data.layers),
            ("obsm", data.obsm),
            ("obsp", data.obsp),
            ("varm", data.varm),
            ("varp", data.varp),
            ("uns", data.uns),
        ):
            for name, obj in container.items():
                generalLogger.debug(f"  ↳ writing {base}:{name}")
                values[base][name] = obj

                if progressBar:
                    progressBar.update()

    if progressBar:
        progressBar.close()

    generalLogger.debug("⎿ VData write to zarr : end ------------------------------------------------------- ")


def write_vdata(
    data: VData | VDataView,
    store: StoreLike,
    path: str | None = None,
    verbose: bool = True,
) -> ez.EZDict[Any]:
    """
    Save a VData object to a local file system.

    Args:
        data: a VData or VDataView to save
        store: Store, path to a directory or name of a zip file.
        path: path within the store to open.
        verbose: print a progress bar while saving objects in this VData ? (default: True)
    """
    if data.data is not None:
        if data.data.group.store == store:
            return data.data

    ez_data = ez.EZDict[Any].open(store, path=path)

    write_vdata_in_ezdict(data, ez_data, verbose=verbose)

    return ez_data


def write_vdata_to_csv(
    data: VData | VDataView,
    directory: str | Path,
    sep: str = ",",
    na_rep: str = "",
    index: bool = True,
    header: bool = True,
) -> None:
    """
    Save layers, timepoints, obs, obsm, obsp, var, varm and varp to csv files in a directory.

    Args:
        directory: path to a directory for saving the matrices
        sep: delimiter character
        na_rep: string to replace NAs
        index: write row names ?
        header: Write col names ?
    """
    directory = Path(directory).expanduser()

    # make sure the directory exists and is empty
    directory.mkdir(parents=True, exist_ok=True)

    if len(list(directory.iterdir())):
        raise IOError("The directory is not empty.")

    # save metadata
    with open(directory / ".metadata.json", "w") as metadata:
        json.dump(
            {
                "obs": {"timepoints_column_name": data.obs.timepoints_column_name},
                "obsm": {
                    obsm_TDF_name: {
                        "timepoints_column_name": obsm_TDF.get_timepoints_column_name(),
                        "col_dtype": str(obsm_TDF.columns.dtype),
                    }
                    for obsm_TDF_name, obsm_TDF in data.obsm.items()
                },
                "layers": {
                    layer_TDF_name: {
                        "timepoints_column_name": layer_TDF.get_timepoints_column_name(),
                        "col_dtype": str(layer_TDF.columns.dtype),
                    }
                    for layer_TDF_name, layer_TDF in data.layers.items()
                },
            },
            metadata,
        )

    # save matrices
    generalLogger.info(f"{spacer(1)}Saving TemporalDataFrame obs")
    data.obs.to_csv(directory / "obs.csv", sep=sep, na_rep=na_rep, index=index, header=header)
    generalLogger.info(f"{spacer(1)}Saving TemporalDataFrame var")
    data.var.to_csv(directory / "var.csv", sep=sep, na_rep=na_rep, index=index, header=header)
    generalLogger.info(f"{spacer(1)}Saving TemporalDataFrame time-points")
    data.timepoints.to_csv(directory / "timepoints.csv", sep=sep, na_rep=na_rep, index=index, header=header)

    for dataset in (data.layers, data.obsm, data.obsp, data.varm, data.varp):
        generalLogger.info(f"{spacer(1)}Saving {dataset.name}")
        dataset.to_csv(directory, sep, na_rep, index, header, spacer=spacer(2))

    if len(data.uns):
        generalLogger.warning(f"'uns' data stored in VData '{data.name}' cannot be saved to a csv.")
