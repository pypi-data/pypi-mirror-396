from __future__ import annotations

from dataclasses import dataclass

import numpy.typing as npt
import pandas as pd

# from h5dataframe import EZDataFrame
from vdata._typing import np_IFS


@dataclass
class LazyLoc:
    h5df: EZDataFrame
    loc: npt.NDArray[np_IFS] | tuple[npt.NDArray[np_IFS], npt.NDArray[np_IFS]]

    @property
    def shape(self) -> tuple[int, int]:
        if not isinstance(self.loc, tuple):
            return len(self.loc), self.h5df.shape[1]

        if len(self.loc) == 1:
            return len(self.loc[0]), self.h5df.shape[1]

        return len(self.loc[0]), len(self.loc[1])

    def get(self) -> EZDataFrame:
        return self.h5df.loc[self.loc]

    def copy(self, deep: bool = True) -> pd.DataFrame:
        return self.get().copy(deep=deep)
