from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import ch5mpy as ch
import ezarr as ez
import zarr

from vdata.update.array import update_array


def _update_dict_v0_to_v1(obj: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:  # pyright: ignore[reportUnusedParameter]
    for key in obj.keys():
        if isinstance(obj @ key, ch.H5Array):
            update_array[0](obj @ key, output_file)  # pyright: ignore[reportArgumentType]

        elif isinstance(obj @ key, ch.H5Dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            _update_dict_v0_to_v1(obj @ key, output_file)


def _update_dict_v1_to_v2(obj: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:  # pyright: ignore[reportUnusedParameter]
    return


def _update_dict_v2_to_v3(obj: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None:
    assert output_file is not None

    if len(obj.attributes):
        ez_data = ez.EZDict[Any](zarr.open_group(output_file, path=obj.file.name))
        ez_data.attrs.put(obj.attributes.as_dict())

    for key in obj.keys():
        if isinstance(obj @ key, ch.H5Array):
            update_array[2](obj @ key, output_file, **kwargs)  # pyright: ignore[reportArgumentType]

        elif isinstance(obj @ key, ch.H5Dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            _update_dict_v2_to_v3(obj @ key, output_file, **kwargs)


class dict_updator(Protocol):
    def __call__(self, obj: ch.H5Dict[Any], output_file: Path | None, **kwargs: Any) -> None: ...


update_dict: list[dict_updator] = [
    _update_dict_v0_to_v1,
    _update_dict_v1_to_v2,
    _update_dict_v2_to_v3,
]
