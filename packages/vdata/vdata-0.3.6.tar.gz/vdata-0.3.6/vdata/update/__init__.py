import importlib

try:
    importlib.import_module("h5dataframe")

except ModuleNotFoundError:
    raise ImportError("vdata.update is not available, please install `vdata[update]`")

from vdata.update.update import update_vdata  # noqa: I001


__all__ = [
    "update_vdata",
]
