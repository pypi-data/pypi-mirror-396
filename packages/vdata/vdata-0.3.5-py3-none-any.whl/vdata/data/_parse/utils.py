import pandas as pd

from vdata.IO.logger import generalLogger
from vdata.utils import repr_array


def log_timepoints(timepoints: pd.DataFrame) -> None:
    generalLogger.debug(f"  {len(timepoints)} time point{' was' if len(timepoints) == 1 else 's were'} found finally.")
    generalLogger.debug(
        f"    \u21b3 Time point{' is' if len(timepoints) == 1 else 's are'} : {repr_array(list(timepoints.value)) if len(timepoints) else '[]'}"
    )
