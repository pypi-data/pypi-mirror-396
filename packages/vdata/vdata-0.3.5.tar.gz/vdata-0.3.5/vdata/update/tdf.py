from __future__ import annotations

import pickle
import warnings
from pathlib import Path
from typing import Any, Callable, Protocol

import ch5mpy as ch
import ezarr as ez
import numpy as np
import zarr
from ezarr.names import Attribute, EZType
from zarr.errors import UnstableSpecificationWarning

import vdata
from vdata.timepoint import TimePointIndex, TimePointNArray, TimePointZArray
from vdata.timepoint.array import as_timepointarray
from vdata.update.array import update_array
from vdata.update.utils import save_class_info


def _update_tdf_v0_to_v1(data: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:  # pyright: ignore[reportUnusedParameter]
    if output_file is not None:
        raise NotImplementedError

    data.attributes.set(
        __h5_type__="object",
        __h5_class__=np.void(pickle.dumps(vdata.TemporalDataFrame, protocol=pickle.HIGHEST_PROTOCOL)),
    )

    del data.attributes["type"]

    if data.attributes["timepoints_column_name"] in ("__ATTRIBUTE_None__", "__TDF_None__"):
        data.attributes["timepoints_column_name"] = "__h5_NONE__"

    data.file.move("timepoints", "timepoints_array")
    data.file.move("values_numerical", "numerical_array")
    data.file.move("values_string", "string_array")

    for array_data in data.values():
        update_array[0](array_data, output_file)


def _update_tdf_v1_to_v2(data: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:  # pyright: ignore[reportUnusedParameter]
    if output_file is not None:
        raise NotImplementedError

    if data.attributes["timepoints_column_name"] is None:
        data.attributes["timepoints_column_name"] = "__h5_NONE__"

    timepoints_index = TimePointIndex.from_array(as_timepointarray(data.timepoints_array))

    data["timepoints_index"] = {
        "ranges": timepoints_index.ranges,
        "timepoints": {
            "array": timepoints_index.timepoints,
        },
    }

    data["timepoints_index"].attributes.set(
        __h5_type__="object",
        __h5_class__=np.void(pickle.dumps(TimePointIndex, protocol=pickle.HIGHEST_PROTOCOL)),
    )
    (data @ "timepoints_index" @ "timepoints").attributes.set(
        __h5_type__="object",
        __h5_class__=np.void(pickle.dumps(TimePointNArray, protocol=pickle.HIGHEST_PROTOCOL)),
        unit=data["timepoints_array"][0][-1],
    )

    del data["timepoints_array"]


def _update_tdf_v2_to_v3(data: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:
    assert output_file is not None
    ez_data = ez.EZDict[Any](zarr.open_group(output_file, path=data.file.name))

    ez_data.attrs.put(
        {
            "name": data.attributes["name"],
            "timepoints_column_name": data.attributes["timepoints_column_name"],
            "repeating_index": bool(data.attributes["repeating_index"]),
            "locked_indices": bool(data.attributes["locked_indices"]),
            "locked_columns": bool(data.attributes["locked_columns"]),
        }
    )

    compressors = kwargs.get("compressors")
    with ez_data.parameters(compressors):
        ez_data["timepoints_index"] = {
            "timepoints": data @ "timepoints_index" @ "timepoints",
            "ranges": data @ "timepoints_index" @ "ranges",
        }
        save_class_info(TimePointIndex, ez_data["timepoints_index"])

        (ez_data @ "timepoints_index" @ "timepoints").attrs.put(  # pyright: ignore[reportOperatorIssue]
            {"unit": str(data["timepoints_index"]["timepoints"].attributes["unit"])}
        )
        save_class_info(TimePointZArray, ez_data @ "timepoints_index" @ "timepoints")  # pyright: ignore[reportOperatorIssue]

        ez_data["index"] = data @ "index"
        ez_data["columns_numerical"] = data @ "columns_numerical"
        ez_data["columns_string"] = data @ "columns_string"
        ez_data["array_numerical"] = data @ "numerical_array"
        ez_data["array_string"] = data @ "string_array"

    save_class_info(vdata.TemporalDataFrame, ez_data)


class tdf_updator(Protocol):
    def __call__(self, data: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None: ...


update_tdf: list[tdf_updator] = [
    _update_tdf_v0_to_v1,
    _update_tdf_v1_to_v2,
    _update_tdf_v2_to_v3,
]
