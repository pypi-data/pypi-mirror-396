from .._backend import DatetimeIndexSplitter
from .._docstrings import docs
from ..types import DatetimeIterable, DatetimeSplits, ExpandLimits, Filter, Schedule, Span


@docs
def split(
    schedule: Schedule,
    *,
    before: Span = "7d",
    after: Span = 1,
    step: int = 1,
    n_splits: int = 0,
    available: DatetimeIterable | None = None,
    expand_limits: ExpandLimits = "auto",
    filter: Filter | str | None = None,
    ignore_filters: bool = False,
) -> DatetimeSplits:
    """Create time-based cross-validation splits.

    To visualize the folds, pass the same arguments to the :func:`.plot`-function.

    Args:
        schedule: {schedule}
        before: {before}
        after: {after}
        step: {step}
        n_splits: {n_splits}
        available: {available} Passing a tuple ``(min, max)`` is enough.
        expand_limits: {expand_limits}
        filter: {filter}
        ignore_filters: {ignore_filters}

    {USER_GUIDE}

    Returns:
        A list of tuples ``[(start, mid, end), ...]``.

    Examples:
        .. minigallery:: time_split.split
    """
    return DatetimeIndexSplitter(
        schedule,
        before=before,
        after=after,
        step=step,
        n_splits=n_splits,
        expand_limits=expand_limits,
        filter=filter,
        ignore_filters=ignore_filters,
    ).get_splits(available)
