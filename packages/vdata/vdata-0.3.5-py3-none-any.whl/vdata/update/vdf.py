from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Protocol

import ch5mpy as ch
import ezarr as ez
import numpy as np
import numpy.typing as npt
import zarr
from ezarr.dataframe import EZDataFrame
from h5dataframe import H5DataFrame

import vdata.timepoint as tp
from vdata.update.array import update_array
from vdata.update.utils import save_class_info


def get_common_dtype(dt1: npt.DTypeLike, dt2: npt.DTypeLike) -> type[np.generic]:
    match dt1, dt2:
        case np.int_, np.int_:
            return np.int64

        case np.float64 | np.int_, np.float64 | np.int_:
            return np.float64

        case _:
            return np.str_


def _update_vdf_v0_to_v1(data: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:  # pyright: ignore[reportUnusedParameter]
    data.attributes.set(
        __h5_type__="object",
        __h5_class__=np.void(pickle.dumps(H5DataFrame, protocol=pickle.HIGHEST_PROTOCOL)),
    )
    del data.attributes["type"]

    data["arrays"] = {}

    if "data_numeric" in data.keys():
        update_array[0](data["data_numeric"]["data"], output_file)
        for col_idx, column in enumerate(data["data_numeric"]["columns"].astype(str)):
            data["arrays"][column] = data["data_numeric"]["data"][:, col_idx].flatten()

        data_num_dtype = data["data_numeric"]["columns"].dtype
        del data["data_numeric"]

    else:
        data_num_dtype = np.int64

    if "data_str" in data.keys():
        update_array[0](data["data_str"]["data"], output_file)
        for col_idx, column in enumerate(data["data_str"]["columns"].astype(str)):
            data["arrays"][column] = data["data_str"]["data"][:, col_idx].flatten()

        data_str_dtype = data["data_str"]["columns"].dtype
        del data["data_str"]

    else:
        data_str_dtype = np.int64

    del data["columns"]

    data.attributes["columns_dtype"] = get_common_dtype(data_num_dtype, data_str_dtype)

    update_array[0](data["index"], output_file)


def _update_vdf_v1_to_v2(data: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:  # pyright: ignore[reportUnusedParameter]
    return


def _update_vdf_v2_to_v3(data: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:
    assert output_file is not None
    ez_data = ez.EZDict[Any](zarr.open_group(output_file, path=data.file.name))

    is_timepoints = ez_data.group.basename == "timepoints"

    compressors = kwargs.get("compressors")
    with ez_data.parameters(compressors):
        ez_data["index"] = data @ "index"
        ez_data["arrays"] = {
            name: arr for name, arr in (data @ "arrays").items() if not is_timepoints or not name == "value"
        }
        ez_data["arrays"].attrs.put(
            {"columns_order": [name for name in (data @ "arrays").keys() if not is_timepoints or not name == "value"]}
        )

        if is_timepoints:
            tps = tp.as_timepointarray(data["arrays"]["value"])
            ez_data["arrays"]["value"] = np.array(tps)
            ez_data["arrays"]["unit"] = np.repeat(tps.unit, len(tps))

            ez_data["arrays"].attrs["columns_order"] = ["value", "unit"] + ez_data["arrays"].attrs["columns_order"]

        save_class_info(EZDataFrame, ez_data)


class vdf_updator(Protocol):
    def __call__(self, data: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None: ...


update_vdf: list[vdf_updator] = [
    _update_vdf_v0_to_v1,
    _update_vdf_v1_to_v2,
    _update_vdf_v2_to_v3,
]
