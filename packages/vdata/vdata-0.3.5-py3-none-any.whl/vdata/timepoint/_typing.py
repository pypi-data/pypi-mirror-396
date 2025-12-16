from typing import Literal

import numpy as np

from vdata.timepoint.timepoint import TimePoint

TIME_UNIT = Literal["s", "m", "h", "D", "M", "Y"]

type TimePointLike = TimePoint | int | float | np.integer | np.floating | bool | str | bytes
