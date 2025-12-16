from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Protocol

import ch5mpy as ch
import numpy as np
import zarr
from zarr.errors import UnstableSpecificationWarning


def _update_array_v0_to_v1(arr: ch.H5Array[Any], output_file: Path | None, **kwargs: Any) -> None:  # pyright: ignore[reportUnusedParameter]
    if output_file is not None:
        raise NotImplementedError

    if arr.dtype == object or np.issubdtype(arr.dtype, bytes):
        arr.attributes["dtype"] = "str"


def _update_array_v1_to_v2(arr: ch.H5Array[Any], output_file: Path | None, **kwargs: Any) -> None:  # pyright: ignore[reportUnusedParameter]
    return


def _update_array_v2_to_v3(arr: ch.H5Array[Any], output_file: Path | None, **kwargs: Any) -> None:
    assert output_file is not None
    compressors = kwargs.get("compressors")

    with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
        zarr.create_array(output_file, name=arr.dset.name, data=np.array(arr), compressors=compressors)


class array_updator(Protocol):
    def __call__(self, arr: ch.H5Array[Any], output_file: Path | None, **kwargs: Any) -> None: ...


update_array: list[array_updator] = [
    _update_array_v0_to_v1,
    _update_array_v1_to_v2,
    _update_array_v2_to_v3,
]
