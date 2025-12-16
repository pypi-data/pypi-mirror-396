from __future__ import annotations

from collections.abc import MutableMapping
from typing import override

import ezarr as ez
import numpy as np

from vdata.data.arrays.base import VTDFArrayContainer
from vdata.data.arrays.view import VTDFArrayContainerView
from vdata.IO import IncoherenceError, ShapeError, generalLogger
from vdata.tdf import TemporalDataFrame, TemporalDataFrameBase, TemporalDataFrameView


class VLayersArrayContainer(VTDFArrayContainer):
    """
    Class for layers.
    This object contains any number of TemporalDataFrames, with shapes (n_timepoints, n_obs, n_var).
    The arrays-like objects can be accessed from the parent VData object by :
        VData.layers[<array_name>]
    """

    @override
    def _check_init_data(
        self, data: MutableMapping[str, TemporalDataFrame | TemporalDataFrameView]
    ) -> MutableMapping[str, TemporalDataFrame | TemporalDataFrameView]:
        """
        Function for checking, at VLayerArrayContainer creation, that the supplied data has the correct format :
            - the shape of the TemporalDataFrames in 'data' match the parent VData object's shape.
            - the index of the TemporalDataFrames in 'data' match the index of the parent VData's obs TemporalDataFrame.
            - the column names of the TemporalDataFrames in 'data' match the index of the parent VData's var DataFrame.
            - the time points of the TemporalDataFrames in 'data' match the index of the parent VData's time-points
            DataFrame.

        Args:
            data: optional dictionary of TemporalDataFrames.

        Returns:
            The data (dictionary of TemporalDataFrames), if correct.
        """
        if not len(data):
            generalLogger.debug("  No data was given.")
            return data if isinstance(data, ez.EZDict) else {}

        generalLogger.debug("  Data was found.")

        _shape = (self._vdata.timepoints.shape[0], self._vdata.obs.shape[1], self._vdata.var.shape[0])
        _data: MutableMapping[str, TemporalDataFrame | TemporalDataFrameView] = (
            {} if not isinstance(data, ez.EZDict) else data
        )

        generalLogger.debug(f"  Reference shape is {_shape}.")

        for TDF_index, tdf in data.items():
            TDF_shape = tdf.shape

            generalLogger.debug(f"  Checking TemporalDataFrame '{TDF_index}' with shape {TDF_shape}.")

            # check that shapes match
            if _shape[0] != TDF_shape[0]:
                raise IncoherenceError(
                    f"Layer '{TDF_index}' has {TDF_shape[0]} time point{'s' if TDF_shape[0] > 1 else ''}, should have {_shape[0]}."
                )

            elif _shape[1] != TDF_shape[1]:
                for i in range(len(tdf.timepoints)):
                    if _shape[1][i] != TDF_shape[1][i]:
                        raise IncoherenceError(
                            f"Layer '{TDF_index}' at time point {i} has {TDF_shape[1][i]} observations, should have {_shape[1][i]}."
                        )

            elif _shape[2] != TDF_shape[2]:
                raise IncoherenceError(f"Layer '{TDF_index}' has  {TDF_shape[2]} variables, should have {_shape[2]}.")

            # check that indexes match
            if np.any(self._vdata.obs.index != tdf.index):
                raise IncoherenceError(
                    f"Index of layer '{TDF_index}' ({tdf.index}) does not match obs' index. ({self._vdata.obs.index})"
                )

            if np.any(self._vdata.var.index != tdf.columns):
                raise IncoherenceError(
                    f"Column names of layer '{TDF_index}' ({tdf.columns}) do not match var's index. ({self._vdata.var.index})"
                )

            if not np.all(self._vdata.timepoints_values == tdf.timepoints):
                raise IncoherenceError(
                    f"Time points of layer '{TDF_index}' ({tdf.timepoints}) do not match time_point's index. ({self._vdata.timepoints.value.values})"
                )

            tdf.lock_indices()
            tdf.lock_columns()

            if isinstance(data, dict):
                _data[str(TDF_index)] = tdf

        generalLogger.debug("  Data was OK.")
        return _data

    @override
    def __setitem__(self, key: str, value: TemporalDataFrameBase) -> None:
        """
        Set a specific TemporalDataFrame in _data. The given TemporalDataFrame must have the correct shape.

        Args:
            key: key for storing a TemporalDataFrame in this VObsmArrayContainer.
            value: a TemporalDataFrame to store.
        """
        if not isinstance(value, TemporalDataFrame):
            raise TypeError(f"Cannot set {self.name} '{key}' from non TemporalDataFrame object.")

        if not self.one_shape == value.shape:
            raise ShapeError(f"Cannot set {self.name} '{key}' because of shape mismatch.")

        if not np.array_equal(self._vdata.var.index, value.columns):
            raise ValueError("Column names do not match.")

        value_copy = value.copy()
        value_copy.name = key
        value_copy.lock_indices()
        value_copy.lock_columns()

        super().__setitem__(key, value_copy)

    @property
    def one_shape(self) -> tuple[int, list[int], int]:
        """Shape of one layer."""
        _shape = self.shape
        return _shape[1], _shape[2], _shape[3][0]


class VLayersArrayContainerView(VTDFArrayContainerView):
    """View on a layer container."""
