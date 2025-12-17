"""Types related to splitting data."""

import datetime as _dt
import logging as _logging
import typing as _t
from abc import ABC as _ABC
from collections import abc as _abc

import numpy as _np
import pandas as _pd

DatetimeTypes: _t.TypeAlias = str | _pd.Timestamp | _dt.datetime | _dt.date | _np.datetime64
"""Types that may be cast to :class:`pandas.Timestamp`."""
DatetimeIterable = _abc.Iterable[DatetimeTypes]
"""Iterable that may be cast to :class:`pandas.DatetimeIndex`."""
TimedeltaTypes: _t.TypeAlias = str | _pd.Timedelta | _dt.timedelta | _np.timedelta64
"""Types that may be cast to :class:`pandas.Timedelta`."""

Schedule: _t.TypeAlias = _pd.DatetimeIndex | DatetimeIterable | TimedeltaTypes
"""User schedule type."""
Span = int | _t.Literal["all", "empty"] | TimedeltaTypes
"""User span type. Used to determine limits from the timestamps given by a :attr:`Schedule`."""
ExpandLimits = bool | _t.Literal["auto"] | str
"""Limits flexibility spec for ``floor/ceil``. Pass ``False`` to disable."""

Filter = _t.Callable[[_pd.Timestamp, _pd.Timestamp, _pd.Timestamp], bool]
"""A callable ``(start, mid, end) -> bool`` used to filter folds."""


class DatetimeSplitBounds(_t.NamedTuple):
    """A 3-tuple which denotes two adjacent datetime ranges."""

    start: _pd.Timestamp
    """Left (inclusive) limit of the `data` range."""
    mid: _pd.Timestamp
    """Schedule timestamp; simulated :attr:`~.DatetimeSplit.training_date`.

    Right (exclusive) limit of the `data` range, left (inclusive) limit of the `future_data` range.

    When using :mod:`.integration` functions, These are available as :attr:`.DatetimeSplit.data` and
    :attr:`.DatetimeSplit.future_data`, respectively.
    """
    end: _pd.Timestamp
    """Right (exclusive) limit of the `future_data` range."""


DatetimeSplits = list[DatetimeSplitBounds]
"""A list of bounds."""


class DatetimeSplitCounts(_t.NamedTuple):
    """Relative importance of `data` and `future_data`."""

    data: int
    future_data: int


class DatetimeIndexSplitterKwargs(_t.TypedDict, total=False):
    """Keyword arguments for :class:`~time_split.support.DatetimeIndexSplitter`.

    The ``DatetimeIndexSplitter`` is a backend implementation. In most cases, it should not be used directly. See
    :func:`time_split.split` or one of the related functions for user-facing APIs.
    """

    schedule: _t.Required[Schedule]
    before: Span
    after: Span
    step: int
    n_splits: int
    expand_limits: ExpandLimits
    filter: Filter | str | None


LogSplitProgressLoggerArg = _logging.Logger | _logging.LoggerAdapter[_t.Any] | str
"""A logger or string."""
MetricsType = _t.TypeVar("MetricsType")
"""Metrics argument type."""
GetMetrics = _t.Callable[[_pd.Timestamp], MetricsType]
"""A callable ``(Timestamp) -> MetricsType``."""
FormatMetrics = _t.Callable[[str, MetricsType], str]
"""A callable ``(end_message, metrics) -> str``."""


class LogSplitProgressKwargs(_t.TypedDict, _t.Generic[MetricsType], total=False):
    """Keyword arguments for by :func:`.log_split_progress`."""

    logger: LogSplitProgressLoggerArg
    start_level: int
    end_level: int
    extra: dict[str, _t.Any] | None
    get_metrics: GetMetrics[MetricsType]


class SplitProgressExtras(_t.TypedDict, _t.Generic[MetricsType]):
    """Named `extras` used for messages logged by :func:`.log_split_progress`."""

    n: int
    """Current split number (starting at 1)."""
    n_splits: int
    """Total split count."""
    start: str
    """An :meth:`ISO-formatted <pandas.Timestamp.isoformat>` timestamp (see :attr:`.DatetimeSplitBounds.start`)."""
    mid: str
    """An :meth:`ISO-formatted <pandas.Timestamp.isoformat>` timestamp (see :attr:`.DatetimeSplitBounds.mid`)."""
    end: str
    """An :meth:`ISO-formatted <pandas.Timestamp.isoformat>` timestamp (see :attr:`.DatetimeSplitBounds.end`)."""
    seconds: _t.NotRequired[float]
    """User time for the fold. Available only for the :attr:`fold-end message <.settings.log_split_progress.END_MESSAGE>`."""
    metrics: _t.NotRequired[MetricsType]
    """Optional fold metrics. Typically appended to the :attr:`fold-end message <.settings.log_split_progress.END_MESSAGE>`."""


class LogSplitProgress(_ABC, _abc.Sequence[DatetimeSplitBounds]):
    """The sequence-like return type of :func:`.log_split_progress`.

    A sequence ``[(start, mid, end), ...]`` which logs progress when iterating.
    """

    splits: _abc.Sequence[DatetimeSplitBounds]
    """The underlying splits."""

    logger: _logging.Logger | _logging.LoggerAdapter  # type: ignore[type-arg]
    """Logger instance that emits messages."""
