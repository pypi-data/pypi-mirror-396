"""Internal types."""

from time_split._backend._schedule import MaterializedSchedule

from .._backend import DatetimeIndexLike, ProcessAvailableResult

__all__ = [
    "DatetimeIndexLike",
    "MaterializedSchedule",
    "ProcessAvailableResult",
]
