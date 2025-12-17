from dataclasses import asdict, dataclass
from typing import cast, get_args

from pandas import Timedelta
from rics.misc import format_kwargs, get_by_full_name

from ..settings import misc as settings
from ..types import (
    DatetimeIndexSplitterKwargs,
    DatetimeIterable,
    DatetimeSplitBounds,
    DatetimeSplits,
    ExpandLimits,
    Filter,
    Schedule,
    Span,
    TimedeltaTypes,
)
from ._schedule import MaterializedSchedule, materialize_schedule
from ._span import OffsetCalculator, to_strict_span


@dataclass(frozen=True)
class DatetimeIndexSplitter:
    """Backend interface for splitting user data. See the :ref:`Parameter overview` page."""

    schedule: Schedule
    before: Span = "7d"
    after: Span = 1
    step: int = 1
    n_splits: int = 0
    expand_limits: ExpandLimits = "auto"
    ignore_filters: bool = False
    filter: Filter | str | None = None

    def get_splits(self, available: DatetimeIterable | None = None) -> DatetimeSplits:
        """Compute a split of given user data."""
        ms = self._materialize_schedule(available)
        return self._make_bounds_list(ms)

    def get_plot_data(self, available: DatetimeIterable | None = None) -> tuple[DatetimeSplits, MaterializedSchedule]:
        """Returns additional data needed to visualize folds."""
        ms = self._materialize_schedule(available)
        splits = self._make_bounds_list(ms)
        return splits, ms

    def _materialize_schedule(self, available: DatetimeIterable | None = None) -> MaterializedSchedule:
        ms = materialize_schedule(self.schedule, self.expand_limits, available=available)
        if not ms.schedule.sort_values().equals(ms.schedule):
            raise ValueError(f"schedule must be sorted in ascending order; schedule={self.schedule!r} is not valid.")

        types = get_args(TimedeltaTypes)
        if (
            settings.snap_to_end
            and self.after not in {"all", "empty"}
            and ms.schedule_type == "timedelta"
            and isinstance(self.after, (types, int))
        ):
            ms = self._snap_to_end(ms)

        return ms

    def _snap_to_end(self, ms: MaterializedSchedule) -> MaterializedSchedule:
        data_end = ms.available_metadata.expanded_limits[1]
        schedule_end = ms.schedule[-1]

        from_end = data_end - schedule_end
        if not isinstance(self.after, int):
            after = Timedelta(self.after)
            from_end -= after

        return ms._replace(schedule=ms.schedule + from_end)

    def _make_bounds_list(self, ms: MaterializedSchedule) -> DatetimeSplits:
        oc_start = OffsetCalculator(self.before, ms.schedule, ms.available_metadata.expanded_limits, name="before")
        oc_end = OffsetCalculator(self.after, ms.schedule, ms.available_metadata.expanded_limits, name="after")

        retval = []
        for i, mid in enumerate(ms.schedule):
            start = oc_start.get(i)
            if start is None:
                continue

            end = oc_end.get(i)
            if end is None:
                continue

            retval.append(DatetimeSplitBounds(start, mid, end))

        if not retval:
            limits_info = f"limits={tuple(map(str, ms.available_metadata.limits))} and "
            msg = f"No valid splits with {limits_info}split params: ({format_kwargs(self.as_dict())})"
            raise ValueError(msg)

        return retval if self.ignore_filters else self._filter(retval)

    def _filter(self, splits: DatetimeSplits) -> DatetimeSplits:
        """Apply splitting arguments.

        Args:
            splits: Splits to filter.

        Returns:
            Filtered splits.
        """
        if self.step != 1:
            step = abs(self.step)
            splits = [s for i, s in enumerate(reversed(splits)) if i % step == 0]
            splits.reverse()

        if self.n_splits > 0:
            splits = splits[-self.n_splits :]

        if self.step < 0:  # Poorly documented - might not work as expected?
            splits.reverse()

        filter = self.filter
        if filter is None:
            return splits

        if isinstance(filter, str):
            filter = cast(Filter, get_by_full_name(filter))

        return [s for s in splits if filter(*s)]

    def __post_init__(self) -> None:
        # Verify n_splits
        if self.n_splits < 0:
            raise ValueError(f"Expected n_splits >= 0, but got n_splits={self.n_splits!r}.")

        # Verify before/after
        to_strict_span(self.before, name="before")
        to_strict_span(self.after, name="after")

        if self.step == 0:
            raise ValueError(f"Bad argument step={self.step}; must be a non-zero integer.")

    def as_dict(self) -> DatetimeIndexSplitterKwargs:
        """Returns the splitter as a ``dict``."""
        return cast(DatetimeIndexSplitterKwargs, asdict(self))
