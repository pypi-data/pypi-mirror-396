from __future__ import annotations

import shutil
from collections.abc import Collection, Mapping, Sequence
from itertools import islice
from math import ceil, floor
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeGuard

import numpy as np
import numpy.typing as npt
import zarr
from tqdm.auto import tqdm

from vdata.array_view import NDArrayView
from vdata.IO.errors import InvalidVDataFileError

if TYPE_CHECKING:
    from vdata._typing import PreSlicer


# misc ------------------------------------------------------------------------
def first_in[V](d: Mapping[Any, V]) -> V:
    return next(iter(d.values()))


def isCollection(obj: Any) -> TypeGuard[Collection[Any]]:
    """
    Whether an object is a collection.

    Args:
        obj: an object to test.
    """
    if isinstance(obj, zarr.Array):
        return True
    return isinstance(obj, Collection) and not isinstance(obj, (str, bytes, bytearray, memoryview))


def are_equal(obj1: Any, obj2: Any) -> bool:
    if isinstance(obj1, (np.ndarray, zarr.Array, NDArrayView)):
        if isinstance(obj2, (np.ndarray, zarr.Array, NDArrayView)):
            return np.array_equal(obj1[:], obj2[:])

        return False

    equality_check = obj1 == obj2
    if isinstance(equality_check, np.ndarray):
        return bool(np.all(equality_check))

    return bool(equality_check)


def spacer(nb: int) -> str:
    return "  " * (nb - 1) + "  " + "\u21b3" + " " if nb else ""


def obj_as_str(arr: npt.NDArray[Any]) -> npt.NDArray[Any]:
    return arr.astype(str) if arr.dtype == object else arr


# representation --------------------------------------------------------------
def repr_array(arr: Any, /, *, n_max: int = 4, print_length: bool = True) -> str:
    """Get a short string representation of an array."""
    if isinstance(arr, slice) or arr is Ellipsis or not isCollection(arr):
        return str(arr)

    if isinstance(arr, np.ndarray):
        arr = arr.tolist()
    else:
        arr = list(arr)

    if len(arr) <= n_max:
        if not print_length:
            return str(arr)
        return f"{str(arr)} ({len(arr)} value{'' if len(arr) == 1 else 's'} long)"

    repr_ = (
        "["
        + " ".join((str(e) for e in islice(arr, 0, ceil(n_max / 2))))
        + " ... "
        + " ".join((str(e) for e in islice(arr, len(arr) - floor(n_max / 2), None)))
        + "]"
    )

    if not print_length:
        return repr_
    return f"{repr_} ({len(arr)} values long)"


def repr_index(
    index: None
    | PreSlicer
    | tuple[PreSlicer | None]
    | tuple[PreSlicer | None, PreSlicer | None]
    | tuple[PreSlicer | None, PreSlicer | None, PreSlicer | None],
) -> str:
    """Get a short string representation of a sub-setting index."""
    if not isinstance(index, tuple):
        index = (index,)

    repr_string = f"Index of {len(index)} element{'' if len(index) == 1 else 's'} : "

    for element in index:
        repr_string += f"\n  \u2022 {repr_array(element) if isCollection(element) else element}"

    return repr_string


# type coercion ---------------------------------------------------------------
def deep_dict_convert(obj: Any) -> dict[Any, Any]:
    """
    'Deep' convert a mapping of any kind (and children mappings) into regular dictionaries.

    Args:
        obj: a mapping to convert.

    Returns:
        a converted dictionary.
    """
    if not isinstance(obj, Mapping):
        return obj

    return {k: deep_dict_convert(v) for k, v in obj.items()}  # pyright: ignore[reportUnknownVariableType]


# copy ------------------------------------------------------------------------
def is_valid_storage(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False

    sub_dir = [p.name for p in path.iterdir()]

    for key in ("layers", "obs", "var", "timepoints", "zarr.json"):
        if key not in sub_dir:
            return False

    return True


def copy_vdata(
    source: str | Path,
    destination: str | Path,
    exclude: list[Literal["obsm", "obsp", "varm", "varp", "uns"]],
    verbose: bool = False,
) -> None:
    source = Path(source)
    destination = Path(destination).with_suffix(".vd")

    if not source.exists():
        raise FileNotFoundError("")

    if not is_valid_storage(source):
        raise InvalidVDataFileError(f"{source} is not a valid stored VData")

    destination.parent.mkdir(parents=True, exist_ok=True)

    # for file in filter(lambda p: p.name not in exclude, source.iterdir()):
    def _ignore(src: str, _) -> Sequence[str]:
        if src == str(source):
            return exclude

        return ()

    if verbose:
        total = (
            sum(
                len([file for file in dir.rglob("*") if file.is_file()])
                for dir in source.iterdir()
                if dir.name not in exclude
            )
            + 1
        )
        progress = tqdm(total=total, desc=f"Copying VData {source}", unit="files")

        def _copy(src: str, dst: str) -> str:
            progress.update()
            return shutil.copy2(src, dst)

        shutil.copytree(source, destination, ignore=_ignore, copy_function=_copy)

    else:
        shutil.copytree(source, destination, ignore=_ignore)
