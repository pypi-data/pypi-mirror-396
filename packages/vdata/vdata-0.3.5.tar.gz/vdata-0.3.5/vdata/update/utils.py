import pickle
import warnings
from typing import Any

import ezarr as ez
import numpy as np
from ezarr.names import Attribute, EZType
from zarr.errors import UnstableSpecificationWarning


def save_class_info(klass: type, ez_data: ez.EZDict[Any]) -> None:
    ez_data.attrs.update(
        {
            Attribute.EZType: EZType.Object,
        }
    )
    with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
        ez_data.create_array(
            Attribute.EZClass,
            data=np.void(pickle.dumps(klass, protocol=pickle.HIGHEST_PROTOCOL)),  # pyright: ignore[reportArgumentType]
            overwrite=True,
        )
