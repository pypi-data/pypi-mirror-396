from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def docs(__func: Callable[P, T], /) -> Callable[P, T]:
    """Add info the docstring of a function."""
    if not __func.__doc__:
        return __func

    offset = "pandas :ref:`offset alias <pandas:timeseries.offset_aliases>`"
    span = (
        f"Range {{}} `schedule` timestamps. Either a {offset}, an integer (`schedule`-based offsets), "
        f"or `'all'` (requires `available` data). Pass `'empty'` to disable."
    )
    docstrings = {
        "schedule": f"A :attr:`~time_split.types.DatetimeIterable`, {offset}, or `cron <https://pypi.org/project/croniter/>`_ expression.",
        "before": span.format("before"),
        "after": span.format("after"),
        "step": "Select a subset of folds, preferring folds later in the schedule.",
        "n_splits": "Maximum number of folds, preferring folds later in the schedule.",
        "available": "Binds `schedule` to a range.",
        "expand_limits": f'A {offset} used to expand `available` data to its likely `"true"` limits. Pass ``False`` to disable.',
        "filter": "A callable ``(start, mid, end) -> bool`` applied to each fold. Strings are converted using :func:`~rics.misc.get_by_full_name`.",
        "ignore_filters": "Set to ignore filtering parameters (e.g. `step` and `filter`).",
        "USER_GUIDE": (
            "For more information about the `schedule`, `before/after` and `expand_limits`-arguments"
            ", see the :ref:`User guide`."
        ),
        "OFFSET": offset,
        "DatetimeIndexSplitterKwargs": "See :func:`~time_split.split`. The `available` keyword is managed by the integration.",
        "show_removed": "If ``True``, splits removed by `n_splits` or `step` are included in the figure.",
        "log_progress": "Controls logging of fold progress. See :func:`~.log_split_progress` for details.",
    }

    __func.__doc__ = __func.__doc__.format(**docstrings)

    return __func
