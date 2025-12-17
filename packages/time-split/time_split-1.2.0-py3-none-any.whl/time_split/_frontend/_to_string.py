import datetime
from typing import Any, Literal, overload

from pandas import Timestamp
from rics.strings import format_seconds as fmt_sec

from .._backend import is_limits_tuple, process_available
from .._backend._limits import LimitsTuple
from ..settings import log_split_progress
from ..types import DatetimeIterable, DatetimeSplitBounds, DatetimeTypes, ExpandLimits


@overload
def to_string(
    bounds: DatetimeSplitBounds | tuple[DatetimeTypes, DatetimeTypes, DatetimeTypes],
    __ignored0: Literal[None] = None,
    __ignored1: Literal[None] = None,
    /,
    *,
    format: str | None = None,
) -> str: ...


@overload
def to_string(
    start: DatetimeTypes,
    mid: DatetimeTypes,
    end: DatetimeTypes,
    /,
    *,
    format: str | None = None,
) -> str: ...


def to_string(
    start_or_bounds: DatetimeTypes | DatetimeSplitBounds | tuple[DatetimeTypes, DatetimeTypes, DatetimeTypes],
    mid: DatetimeTypes | None = None,
    end: DatetimeTypes | None = None,
    /,
    *,
    format: str | None = None,
) -> str:
    """Pretty-print a fold.

    Args:
        start_or_bounds: A fold tuple ``(start, mid, end)``, or just `start` (followed by `mid` and `end`).
        mid: Datetime-like. Must be ``None`` when `start_or_bounds` is a tuple.
        end: Datetime-like. Must be ``None`` when `start_or_bounds` is a tuple.
        format: A custom format to use. Use :attr:`~.settings.log_split_progress.FOLD_FORMAT` if ``None``, but note that
            only the `start`, `mid` and `end` keys are available to this function.

    Returns:
        Formatted bounds string.

    Raises:
        TypeError: If an incorrect number of timestamps are given.

    Examples:
        Sample format output.

        >>> to_string("2021-12-30", "2022-01-04", "2022-01-04 18:00:00")
        "'2021-12-30' <= [schedule: '2022-01-04' (Tuesday)] < '2022-01-04 18:00:00'"

        The :attr:`default format <.log_split_progress.FOLD_FORMAT>` was used above.

        Using properties. The `delta` is the distance from `mid` formatted by
        :func:`~rics.strings.format_seconds`. The `date` property returns a :class:`datetime.date` object.

        >>> to_string(
        ...     ("2021-12-30", "2022-01-04", "2022-01-04 18:00:00"),
        ...     format="'{start.date}' [-{start.delta}] <= '{mid.iso}' < [+{end.delta}]",
        ... )
        "'2021-12-30' [-5d] <= '2022-01-04T00:00:00' < [+18h]"

        The delta is always positive; you must add the sign yourself.
    """
    if isinstance(start_or_bounds, tuple):
        if not (mid is None and end is None):
            raise TypeError(f"Too many arguments: {(start_or_bounds, mid, end)}.")
        start, mid, end = start_or_bounds
    else:
        if mid is None or end is None:
            raise TypeError(f"Too few arguments: {(start_or_bounds, mid, end)}.")
        start = start_or_bounds

    if format is None:
        format = log_split_progress.FOLD_FORMAT

    return format.format(
        start=_PrettyTimestamp(start, mid),
        mid=_PrettyTimestamp(mid, mid),
        end=_PrettyTimestamp(end, mid),
    )


def stringify(old: Timestamp, *, new: Timestamp | None = None, diff_only: bool = False) -> str:
    if new is None:
        return _PrettyTimestamp(old).auto

    original = f"{old} -> "
    if old == new:
        no_change = "<no change>"
        if diff_only:
            return no_change
        return original + no_change
    diff = (new - old).total_seconds()
    pretty_diff = f"{'+' if diff > 0 else '-'}{fmt_sec(abs(diff))}"

    if diff_only:
        return pretty_diff

    return original + f"{_PrettyTimestamp(new).auto} ({pretty_diff})"


class _PrettyTimestamp:
    def __init__(self, raw: DatetimeTypes, anchor: DatetimeTypes | None = None) -> None:
        self.timestamp = Timestamp(raw)
        self._anchor = None if anchor is None else Timestamp(anchor)
        self._auto: str | None = None
        self._delta: str | None = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self.timestamp, name)

    def __str__(self) -> str:
        return str(self.timestamp)

    def __repr__(self) -> str:
        return repr(self.timestamp)

    def __format__(self, format_spec: str) -> str:
        return format(self.timestamp, format_spec)

    @property
    def auto(self) -> str:
        if self._auto is None:
            timestamp = self.timestamp.round("s")
            format_spec = (
                log_split_progress.AUTO_DATE_FORMAT
                if timestamp.normalize() == timestamp
                else log_split_progress.AUTO_DATETIME_FORMAT
            )
            self._auto = format(timestamp, format_spec)
        return self._auto

    @property
    def delta(self) -> str:
        if self._anchor is None:
            raise ValueError("Delta requires an anchor.")

        if self._delta is None:
            seconds = (self.timestamp - self._anchor).round("s").total_seconds()
            self._delta = fmt_sec(abs(seconds))

        return self._delta

    @property
    def iso(self) -> str:
        return self.timestamp.isoformat()  # type: ignore[no-any-return]

    @property
    def date(self) -> datetime.date:
        return self.timestamp.date()  # type: ignore[no-any-return]


def format_expanded_limits(
    original: LimitsTuple | DatetimeIterable,
    *,
    expanded: LimitsTuple | None = None,
    expand_limits: ExpandLimits = "auto",
    raise_if_same: bool = False,
) -> str:
    """Format expanded limits.

    Args:
        original: The original data limits.
        expanded: Expanded data limits. Derived based on `original` and `expanded_limits` if ``None``.
        expand_limits: Limits expansion spec.
        raise_if_same: If ``True``, raise a :exc:`ValueError` if the `original` and `expanded_limits` are not the same.
            Otherwise, a different message will be returned instead.

    Returns:
        A string.

    Raises:
        ValueError: If ``raise_on_same`` is ``True`` and ``original == expanded``.

    Examples:
        Basic usage.

        >>> limits = "2019-05-11", "2019-05-11 22:05:30"
        >>> string = format_expanded_limits(limits, expand_limits="d<3h")
        >>> print(string)
        Available data limits have been expanded (since expand_limits='d<3h'):
          start: 2019-05-11 00:00:00 -> <no change>
            end: 2019-05-11 22:05:30 -> 2019-05-12 (+1h 54m 30s)

        A different message is shown when the limits aren't expanded.

        >>> string = format_expanded_limits(limits, expand_limits="d<1h")
        >>> print(string)
        Original limits ('2019-05-11', '2019-05-11 22:05:30') were not expanded (since expand_limits='d<1h').

        Set ``raise_if_same=True`` to disable the second message.

    See Also:
        The :func:`.process_available` and :func:`.expand_limits` functions.
    """
    if expanded is None:
        if is_limits_tuple(original):
            from .._backend._limits import expand_limits as expand

            expanded = expand(original, spec=expand_limits)
        else:
            result = process_available(original, expand_limits=expand_limits)
            original = result.limits
            expanded = result.expanded_limits

    if not is_limits_tuple(original):
        msg = f"Bad {original=}; not a valid limits tuple."
        raise TypeError(msg)

    if original == expanded:
        left, right = stringify(original[0]), stringify(original[1])
        msg = f"Original limits {(left, right)} were not expanded (since {expand_limits=})."
        if raise_if_same:
            raise ValueError(msg)
        return msg

    return (
        f"Available data limits have been expanded (since {expand_limits=}):\n"
        f"  start: {stringify(original[0], new=expanded[0])}\n"
        f"    end: {stringify(original[1], new=expanded[1])}"
    )
