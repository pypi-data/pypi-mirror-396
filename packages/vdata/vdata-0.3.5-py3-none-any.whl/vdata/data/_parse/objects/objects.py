from typing import Any

from ezarr.dataframe import EZDataFrame

from vdata.data._parse.data import ParsingDataIn, ParsingDataOut
from vdata.data._parse.objects.layers import parse_layers
from vdata.data._parse.objects.obs import parse_obs, parse_obsm, parse_obsp
from vdata.data._parse.objects.uns import parse_uns
from vdata.data._parse.objects.var import parse_varm, parse_varp
from vdata.data._parse.utils import log_timepoints
from vdata.IO.logger import generalLogger
from vdata.tdf import TemporalDataFrameBase


def _valid_timepoints(data: ParsingDataIn, obs: TemporalDataFrameBase) -> Any:  # EZDataFrame:
    if data.timepoints.empty:
        generalLogger.debug("Default empty DataFrame for time points.")
        for row in [(tp.value, tp.unit) for tp in obs.timepoints]:
            data.timepoints.loc[len(data.timepoints)] = row

    log_timepoints(data.timepoints)
    return data.timepoints if isinstance(data.timepoints, EZDataFrame) else EZDataFrame(data.timepoints)


def parse_objects(data: ParsingDataIn) -> ParsingDataOut:
    generalLogger.debug("  VData creation from scratch.")

    parse_layers(data)
    _obs = parse_obs(data)

    return ParsingDataOut(
        data.layers,
        _obs,
        parse_obsm(data),
        parse_obsp(data),
        EZDataFrame(data.var) if not isinstance(data.var, EZDataFrame) else data.var,
        parse_varm(data),
        parse_varp(data),
        _valid_timepoints(data, _obs),
        parse_uns(data),
    )
