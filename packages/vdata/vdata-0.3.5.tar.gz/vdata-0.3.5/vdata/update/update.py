from __future__ import annotations

import shutil
import warnings
from pathlib import Path
from typing import Any

import ch5mpy as ch
import ezarr as ez
import numpy as np
import zarr
from h5dataframe import H5DataFrame
from tqdm.auto import tqdm
from zarr.codecs.numcodecs import LZ4
from zarr.core.array import CompressorsLike
from zarr.errors import ZarrUserWarning

import vdata
from vdata.data.name import WRITE_PROTOCOL_VERSION
from vdata.update.dict import update_dict
from vdata.update.tdf import update_tdf
from vdata.update.vdf import update_vdf


class NoBar:
    def update(self) -> None:
        pass

    def close(self) -> None:
        pass


def _update_vdata(
    data: ch.H5Dict[Any] | ez.EZDict[Any],
    output_file: Path | None,
    *,
    from_version: int,
    progressBar: tqdm[Any] | NoBar,
    compressors: CompressorsLike,
) -> ch.H5Dict[Any] | ez.EZDict[Any]:
    if isinstance(data, ez.EZDict):
        return data

    # layers ------------------------------------------------------------------
    for layer in (data @ "layers").keys():
        update_tdf[from_version]((data @ "layers") @ layer, output_file, compressors=compressors)
        progressBar.update()

    # obs ---------------------------------------------------------------------
    if "obs" not in data.keys():
        first_layer = (data @ "layers")[list((data @ "layers").keys())[0]]

        obs = vdata.TemporalDataFrame(
            index=ch.read_object(first_layer["index"]),
            # repeating_index=first_layer.attrs["repeating_index"],
            timepoints=ch.read_object(first_layer["timepoints_array"]),
        )
        ch.write_object(obs, data, "obs")
    else:
        update_tdf[from_version](data @ "obs", output_file, compressors=compressors)

    progressBar.update()

    for obsm_tdf in (data @ "obsm").keys():
        update_tdf[from_version](data @ "obsm" @ obsm_tdf, output_file, compressors=compressors)
        progressBar.update()

    for obsp_vdf in (data @ "obsp").keys():
        update_vdf[from_version](data @ "obsp" @ obsp_vdf, output_file, compressors=compressors)
        progressBar.update()

    # var ---------------------------------------------------------------------
    if "var" not in data.keys():
        first_layer = (data @ "layers")[list((data @ "layers").keys())[0]]

        var = H5DataFrame(
            index=np.concatenate(
                (ch.read_object(first_layer["columns_numerical"]), ch.read_object(first_layer["columns_string"]))
            )
        )
        ch.write_object(var, data, "var")
    else:
        update_vdf[from_version](data @ "var", output_file, compressors=compressors)

    progressBar.update()

    for varm_vdf in (data @ "varm").keys():
        update_vdf[from_version](data @ "varm" @ varm_vdf, output_file, compressors=compressors)
        progressBar.update()

    for varp_vdf in (data @ "varp").keys():
        update_vdf[from_version](data @ "varp" @ varp_vdf, output_file, compressors=compressors)
        progressBar.update()

    # timepoints --------------------------------------------------------------
    if "timepoints" not in data.keys():
        first_layer = (data @ "layers")[list((data @ "layers").keys())[0]]

        timepoints = H5DataFrame({"value": np.unique(ch.read_object(first_layer["timepoints_array"]))})
        ch.write_object(timepoints, data, "timepoints")
    else:
        update_vdf[from_version](data @ "timepoints", output_file, compressors=compressors)

    progressBar.update()

    # uns ---------------------------------------------------------------------
    if "uns" not in data.keys():
        data["uns"] = {}

    else:
        update_dict[from_version](data @ "uns", output_file, compressors=compressors)

    progressBar.update()

    if from_version == 2:
        return ez.EZDict[Any](zarr.open_group(output_file, path=data.file.name))

    return data


def _get_output_file(data_file: Path, output_file: str | Path | None, from_version: int) -> Path | None:
    if output_file is not None:
        return Path(output_file)

    if from_version < 2:
        return None

    ez_filename = Path("/tmp") / data_file.name
    if from_version == 2:
        if ez_filename.exists():
            raise FileExistsError(f"File '{ez_filename}' already exists")

        ez_filename.mkdir()

    return ez_filename


with warnings.catch_warnings(action="ignore", category=ZarrUserWarning):
    _default_compressors = (LZ4(),)


def update_vdata(
    data: Path | str | ch.H5Dict[Any] | ez.EZDict[Any],
    *,
    output_file: str | Path | None = None,
    verbose: bool = False,
    compressors: CompressorsLike = _default_compressors,
) -> tuple[int, ez.EZDict[Any]]:
    """
    Update a saved vdata from an older version.

    Args:
        data: path to the h5 file to update.
        output_file: path to the updated output vdata file.
        verbose: print a progress bar ? (default: False)
        compressors: zarr compressors to use when writing Arrays. (default: LZ4)
    """
    if isinstance(data, ez.EZDict):
        assert data.attrs.get("__vdata_write_version__") == WRITE_PROTOCOL_VERSION, (
            f"Invalid version, expected '{WRITE_PROTOCOL_VERSION}', got '{data.attrs.get('__vdata_write_version__')}'"
        )
        return WRITE_PROTOCOL_VERSION, data

    if not isinstance(data, ch.H5Dict):
        data = ch.H5Dict.read(data, mode=ch.H5Mode.READ_WRITE)

    if not data.mode.has_write_intent:  # pyright: ignore[reportUnnecessaryComparison]
        raise ValueError(f"Cannot update VData object open in '{data.mode}' mode")

    data_version = data.attributes.get("__vdata_write_version__", 0)

    if data_version > WRITE_PROTOCOL_VERSION:
        raise ValueError(
            f"VData object was written with a version ({data_version}) of the write protocol higher than the current one ({WRITE_PROTOCOL_VERSION})"
        )

    nb_items_to_write = (
        4 + len(data @ "layers") + len(data @ "obsm") + len(data @ "obsp") + len(data @ "varm") + len(data @ "varp")
    )
    filename = data.filename

    for v in range(data_version, WRITE_PROTOCOL_VERSION):
        progressBar: tqdm[Any] | NoBar = (
            tqdm(total=nb_items_to_write, desc=f"Updating VData {filename} [version {v} => {v + 1}]", unit="object")
            if verbose
            else NoBar()
        )

        out = _get_output_file(Path(filename), output_file, v)

        try:
            new_data = _update_vdata(data, out, from_version=v, progressBar=progressBar, compressors=compressors)

        except Exception as e:
            if out is not None:
                if out.is_dir():
                    shutil.rmtree(out)

                else:
                    out.unlink()

            progressBar.close()
            raise e

        if isinstance(new_data, ez.EZDict):
            new_data.attrs["__vdata_write_version__"] = v + 1

            if isinstance(data, ch.H5Dict):
                assert out is not None

                data.close()
                Path(filename).unlink()
                output_file = shutil.move(out, filename)

                new_data = ez.EZDict[Any](zarr.open_group(filename))

        else:
            new_data.attributes["__vdata_write_version__"] = v + 1

        data = new_data

        progressBar.close()

    assert isinstance(data, ez.EZDict)
    return data_version, data
