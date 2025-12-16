"""Annotated, temporal and multivariate observation data."""

from importlib.metadata import metadata
from pathlib import Path

from vdata.data import VData, VDataView, concatenate, convert_anndata_to_vdata
from vdata.data.name import WRITE_PROTOCOL_VERSION
from vdata.IO import IncoherenceError, InvalidVDataFileError, ShapeError, VBaseError, VLockError, VReadOnlyError
from vdata.tdf import RepeatingIndex, TemporalDataFrame, TemporalDataFrameView
from vdata.timepoint import TimePoint
from vdata.utils import copy_vdata

read = VData.read
read_from_csv = VData.read_from_csv
read_from_anndata = VData.read_from_anndata
read_from_pickle = VData.read_from_pickle

__version__ = metadata("vdata").get("version")


def get_version(path: str | Path) -> int:
    import ch5mpy as ch
    import ezarr

    try:
        return ch.H5Dict.read(path).attributes.get("__vdata_write_version__", 0)

    except IsADirectoryError:
        return ezarr.EZDict.open(path).attrs["__vdata_write_version__"]  # pyright: ignore[reportReturnType]


__all__ = [
    "concatenate",
    "convert_anndata_to_vdata",
    "copy_vdata",
    "IncoherenceError",
    "InvalidVDataFileError",
    "RepeatingIndex",
    "ShapeError",
    "TemporalDataFrame",
    "TemporalDataFrameView",
    "TimePoint",
    "VBaseError",
    "VData",
    "VDataView",
    "VLockError",
    "VReadOnlyError",
    "WRITE_PROTOCOL_VERSION",
]
