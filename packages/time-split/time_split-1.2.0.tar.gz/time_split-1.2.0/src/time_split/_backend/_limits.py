from collections.abc import Iterable
from itertools import starmap
from typing import Any, NamedTuple, TypeGuard

from pandas import Timedelta, Timestamp

from ..settings import auto_expand_limits, misc
from ..types import ExpandLimits, TimedeltaTypes

LimitsTuple = tuple[Timestamp, Timestamp]
LevelTuple = tuple[TimedeltaTypes, TimedeltaTypes, TimedeltaTypes]


class _TimedeltaTuple(NamedTuple):
    start_at: Timedelta
    round_to: Timedelta
    tolerance: Timedelta


def is_limits_tuple(arg: Any) -> TypeGuard[LimitsTuple]:
    """Check if `arg` is a :class:`.LimitsTuple`.

    Args:
        arg: An argument.

    Returns:
        Returns ``True`` if `arg` is a :class:`.LimitsTuple`.
    """
    if not (isinstance(arg, tuple) and len(arg) == 2):  # noqa: PLR2004
        return False

    start, end = arg
    if not (isinstance(start, Timestamp) and isinstance(end, Timestamp)):
        return False

    return bool(start <= end)


def expand_limits(
    limits: LimitsTuple,
    spec: ExpandLimits | LevelTuple | Iterable[LevelTuple] = "auto",
) -> LimitsTuple:
    """Derive the `"real"` bounds of `limits`.

    Use :attr:`time_split.settings.misc.round_limits` to allow inward "expansion".

    Args:
        limits: A tuple ``(min, max)`` of timestamps.
        spec: Expansion spec as described in the :ref:`User guide`. Also supports level-tuples
            ``[(start_at, round_to, tolerance)...]``. Passing
            ``expand_limits=[settings.auto_expand_limits.day, settings.auto_expand_limits.hour]``
            is equivalent to ``expand_limits='auto'``.

    Returns:
        Limits rounded according to the given specification.

    Raises:
        ValueError: For invalid limits.

    Examples:
        >>> from pandas import Timestamp
        >>> limits = Timestamp("2019-05-11"), Timestamp("2019-05-11 22:05:30")

        Basic usage.

        >>> expand_limits(limits, "d")
        (Timestamp('2019-05-11 00:00:00'), Timestamp('2019-05-12 00:00:00'))

        You may specify a maximum "distance" that limits may be expanded.

        >>> expand_limits(limits, "d<1h")
        (Timestamp('2019-05-11 00:00:00'), Timestamp('2019-05-11 22:05:30'))

        Limits will never be rounded in the "wrong" direction...

        >>> limits = Timestamp("2019-05-11"), Timestamp("2019-05-11 11:05:30")
        >>> expand_limits(limits, "d")
        (Timestamp('2019-05-11 00:00:00'), Timestamp('2019-05-11 11:05:30'))

        ...even if you make the tolerance large enough.

        >>> expand_limits(limits, "d<14h")
        (Timestamp('2019-05-11 00:00:00'), Timestamp('2019-05-11 11:05:30'))

        To disable this restriction, set :attr:`round_limits=True <.misc.round_limits>` in the settings.
    """
    if limits[0] >= limits[1]:
        msg = f"Bad limits. Expected limits[1] > limits[0], but got {limits=}."
        raise ValueError(msg)

    if spec is False:
        return limits

    if spec is True or spec == "auto":
        return _from_levels(limits)

    if isinstance(spec, str):
        round_to, _, tolerance = spec.partition("<")
        level = _make_level(None, round_to=round_to.strip(), tolerance=tolerance.strip())
        return _apply(limits, level=level)
    if isinstance(spec, tuple):
        return _from_levels(limits, levels=[_make_level(*spec)])

    return _from_levels(limits, levels=starmap(_make_level, spec))


def _from_levels(limits: LimitsTuple, *, levels: Iterable[_TimedeltaTuple] | None = None) -> LimitsTuple:
    if levels is None:
        levels = _levels_from_settings()
    else:
        levels = sorted(levels, reverse=True, key=lambda level: level[0])

    lo, hi = limits
    diff = hi - lo

    for level in levels:
        start_at, _round_to, _tolerance = level
        if diff >= start_at:
            return _apply(limits, level=level)

    return limits


def _apply(limits: LimitsTuple, *, level: _TimedeltaTuple) -> LimitsTuple:
    lo, hi = limits

    round = misc.round_limits
    lo_floor = lo.round(level.round_to) if round else lo.floor(level.round_to)
    if abs(lo_floor - lo) > level.tolerance:
        return limits

    hi_ceil = hi.round(level.round_to) if round else hi.ceil(level.round_to)
    if abs(hi_ceil - hi) > level.tolerance:
        return limits

    if auto_expand_limits.SANITY_CHECK:
        if round:
            if lo_floor == hi_ceil:
                return limits
        else:
            if lo.round(level.round_to) != lo_floor:
                return limits
            if hi.round(level.round_to) != hi_ceil:
                return limits

    return lo_floor, hi_ceil


def _levels_from_settings() -> list[_TimedeltaTuple]:
    day, hour = _make_level(*auto_expand_limits.day), _make_level(*auto_expand_limits.hour)
    if day.round_to != Timedelta(days=1):
        msg = f"Invalid settings: {auto_expand_limits.day=} must have round_to=1 day."
        raise ValueError(msg)
    if hour.round_to != Timedelta(hours=1):
        msg = f"Invalid settings: {auto_expand_limits.hour=} must have round_to=1 hour."
        raise ValueError(msg)
    return [day, hour]


def _make_level(
    start_at: TimedeltaTypes | None,
    round_to: TimedeltaTypes,
    tolerance: TimedeltaTypes,
) -> _TimedeltaTuple:
    start_at = Timedelta(start_at)  # Will be NaT if None, making all ifs False.
    if start_at <= Timedelta(0):
        raise ValueError(f"Bad {start_at=}; must be non-negative.")

    try:
        round_to = Timedelta(1, unit=round_to)
    except ValueError as e:
        raise ValueError(f"Got {round_to=}, which is not a valid frequency.") from e

    tolerance = Timedelta(tolerance)
    if tolerance <= Timedelta(0):
        raise ValueError(f"Bad {tolerance=}; must be non-negative.")

    if start_at < round_to:
        raise ValueError(f"{start_at=} < {round_to=}")
    if round_to < tolerance:
        raise ValueError(f"{round_to=} < {tolerance=}")
    return _TimedeltaTuple(start_at, round_to, tolerance)
