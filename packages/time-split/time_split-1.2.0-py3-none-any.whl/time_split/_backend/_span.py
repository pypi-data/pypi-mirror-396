from collections.abc import Callable
from datetime import timedelta
from typing import Literal, TypeAlias

from pandas import DatetimeIndex, Timedelta, Timestamp

from ..types import Span
from ._limits import LimitsTuple
from ._schedule import NO_LIMITS

StrictSpan: TypeAlias = int | Timedelta | Literal["all", "empty"]
SpanArgumentName = Literal["before", "after"]
FuncType = Callable[[int], Timestamp | None]


class InvalidSpanError(ValueError):
    """Raised when offsets values for 'before' and 'after' arguments are invalid."""

    def __init__(
        self,
        span: Span,
        *,
        name: SpanArgumentName,
        reason: str = "must be greater than zero",
    ) -> None:
        super().__init__(f"Bad '{name}'-argument; offset {span!r} {reason}.")


def _to_timedelta(span: str | timedelta | Timedelta, *, name: SpanArgumentName) -> Timedelta:
    retval = Timedelta(span)
    if retval <= Timedelta(0):
        raise InvalidSpanError(span, name=name)
    return retval


def to_strict_span(span: Span, *, name: SpanArgumentName) -> StrictSpan:
    """Convert `span` to a strict span.

    Args:
        span: User span.
        name: Name of user input. User for error reporting.

    Returns:
        A valid span with reduced types.

    Raises:
        TypeError: For bad `span` types.
        InvalidSpanError: For invalid `span` arguments.

    """
    if span in {"all", "empty"}:
        return span

    if isinstance(span, (str, timedelta, Timedelta)):
        return _to_timedelta(span, name=name)

    if isinstance(span, (int, float)):
        retval = int(span)
        if retval <= 0:
            raise InvalidSpanError(retval, name=name)
        return retval

    raise TypeError(f"cannot parse '{name}'-argument of type {type(span).__name__}: {span!r}.")


class OffsetCalculator:
    """Utility class for computing before/after offsets from the `schedule`."""

    def __init__(
        self,
        span: Span,
        schedule: DatetimeIndex,
        limits: LimitsTuple,
        *,
        name: SpanArgumentName,
    ) -> None:
        span = to_strict_span(span, name=name)
        is_before = name == "before"

        self._schedule = schedule
        self._is_before = is_before
        self._limits: LimitsTuple | None = None if limits == NO_LIMITS else limits

        self._func: FuncType
        if span == "all":
            self._func = self.get_all
        elif span == "empty":
            self._func = self.get_empty
        elif isinstance(span, int):
            self._func = self._make_int(span)
        else:  # Timedelta
            self._func = self._make_timedelta(span)

    def get(self, i: int) -> Timestamp | None:
        """Get get outer bound at index `i`."""
        rv = self._func(i)
        if rv is None:
            return None

        mid = self._schedule[i]

        if self._limits:
            min_start, max_end = self._limits
            if not (min_start <= mid <= max_end):
                return None  # Snapping to end may shift schedule out of range.
            if not (min_start <= rv <= max_end):
                return None

        if rv == mid and self._func != self.get_empty:
            return None

        return rv

    def get_all(self, _: int) -> Timestamp:
        if self._limits is None:
            raise InvalidSpanError("all", name=self.name, reason="requires available data to bound the schedule")

        index = 0 if self._is_before else 1
        return self._limits[index]

    def get_empty(self, i: int) -> Timestamp:
        return self._schedule[i]

    def _make_int(self, offset: int) -> FuncType:
        def func(i: int) -> Timestamp | None:
            i = i - offset if self._is_before else i + offset
            if 0 <= i < len(self._schedule):
                return self._schedule[i]
            else:
                return None

        func.__name__ = f"get_int({offset})"
        return func

    def _make_timedelta(self, offset: Timedelta) -> FuncType:
        if self._is_before:
            schedule = self._schedule - offset
        else:
            schedule = self._schedule + offset

        def func(i: int) -> Timestamp:
            return schedule[i]

        func.__name__ = f"get_timedelta('{offset}')"
        return func

    @property
    def name(self) -> SpanArgumentName:
        return "before" if self._is_before else "after"

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.name}={self._func.__name__})"
