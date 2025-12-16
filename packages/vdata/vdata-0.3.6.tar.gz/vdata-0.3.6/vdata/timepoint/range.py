from __future__ import annotations

import numpy as np

from vdata.timepoint._typing import TIME_UNIT
from vdata.timepoint.timepoint import TimePoint


class TimePointRangeIterator:
    """Iterator over a TimePointRange."""

    __slots__: tuple[str, ...] = "_current", "_stop", "_step"

    def __init__(self, start: TimePoint, stop: TimePoint, step: TimePoint):
        if start.unit != step.unit:
            raise ValueError("Cannot create TimePointRangeIterator if start and step time-points' units are different")

        self._current: TimePoint = start
        self._stop: TimePoint = stop
        self._step: TimePoint = step

    def __iter__(self) -> TimePointRangeIterator:
        return self

    def __next__(self) -> TimePoint:
        if self._current >= self._stop:
            raise StopIteration

        self._current = TimePoint(value=self._current.value + self._step.value, unit=self._current.unit)
        return self._current


class TimePointRange:
    """Range of TimePoints."""

    __slots__: tuple[str, ...] = "_start", "_stop", "_step"

    def __init__(
        self,
        start: np.int_ | int | np.float64 | float | np.str_ | str | TimePoint,
        stop: np.int_ | int | np.float64 | float | np.str_ | str | TimePoint,
        step: np.int_ | int | np.float64 | float | np.str_ | str | TimePoint | None = None,
        unit: TIME_UNIT | None = None,
    ):
        self._start: TimePoint = TimePoint(start, unit=unit)
        self._stop: TimePoint = TimePoint(stop, unit=unit)
        self._step: TimePoint = (
            TimePoint(value=1, unit=self._start.unit) if step is None else TimePoint(step, unit=unit)
        )

        if self._start.unit != self._stop.unit:
            raise ValueError("Cannot create TimePointRange if start and stop units are different.")

        if self._start.unit != self._step.unit:
            raise ValueError("Cannot create TimePointRange if start and step units are different.")

    def __iter__(self) -> TimePointRangeIterator:
        return TimePointRangeIterator(self._start, self._stop, self._step)

    @property
    def unit(self) -> TIME_UNIT:
        return self._start.unit

    @property
    def start(self) -> TimePoint:
        return self._start

    @property
    def stop(self) -> TimePoint:
        return self._stop

    @property
    def step(self) -> TimePoint:
        return self._step
