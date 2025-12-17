"""Base implementations for splitting generic data types.

Users may implement splitting of any data type by implementing suitable ``as_available`` and ``select`` functions.
"""

import typing as _t
from datetime import datetime as _datetime

from .. import _frontend
from .. import types as _tst
from .._docstrings import docs as _docs
from . import _log_progress

if _t.TYPE_CHECKING:
    import pandas

DataT = _t.TypeVar("DataT")
"""Type of data to split."""

DataAsAvailableFn = _t.Callable[[DataT], _tst.DatetimeIterable]
"""A callable ``(data: DataT) -> DatetimeIterable``."""
DataSelectFn = _t.Callable[[DataT, _datetime, _datetime], DataT]
"""A callable ``(data: DataT, left_inclusive: datetime, end_exclusive: datetime) -> DataT)``."""


class DatetimeSplit(_t.NamedTuple, _t.Generic[DataT]):
    """Time-based split of a generic data type."""

    data: DataT
    """Data before the simulated :attr:`training_date`.

    Bounded by `bounds.start <= time(future_data) < bounds.mid`.
    """
    future_data: DataT
    """Data after the simulated :attr:`training_date`.

    Bounded by `bounds.mid <= time(future_data) < bounds.end`.
    """
    bounds: _tst.DatetimeSplitBounds
    """The underlying bounds that produced this split."""

    @property
    def training_date(self) -> "pandas.Timestamp":
        """Returns the simulated training date (alias of :attr:`self.bounds.mid <.DatetimeSplitBounds.mid>`)."""
        return self.bounds.mid


@_docs
def split_data(
    data: DataT,
    *,
    log_progress: _log_progress.LogProgressArg[_tst.MetricsType] = False,
    as_available: DataAsAvailableFn[DataT],
    select: DataSelectFn[DataT],
    **kwargs: _t.Unpack[_tst.DatetimeIndexSplitterKwargs],
) -> _t.Iterable[DatetimeSplit[DataT]]:
    """Base implementation for splitting integrated `data` types.

    The required ``as_available`` and ``select`` callables provided perform the actual integration.

    Args:
        data: The data to split.
        log_progress: {log_progress}
        as_available: A callable ``(data: DataT) -> DatetimeIterable``.
        select: A callable ``(data: DataT, left_inclusive: datetime, end_exclusive: datetime) -> DataT)``.
        **kwargs: Keyword arguments for :func:`.split`-function.

    Yields:
        Tuples ``(data, future_data, bounds)``.

    See Also:
        To get started with your own integration, copy :func:`~time_split.integration.pandas.split_pandas` or
        :func:`~time_split.integration.polars.split_polars` and use it as the baseline (click ``[source]``) on
        the linked function.

    """
    available = as_available(data)
    splits = _frontend.split(**kwargs, available=available)

    tracked_splits = _log_progress.handle_log_progress_arg(log_progress, splits=splits)

    for bounds in splits if tracked_splits is None else tracked_splits:
        yield DatetimeSplit(
            select(data, bounds.start, bounds.mid),
            future_data=select(data, bounds.mid, bounds.end),
            bounds=bounds,
        )
