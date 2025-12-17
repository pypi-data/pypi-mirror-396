"""Supporting functions.

These functions are used internally, but are exposed here as well so that user may create their own logic using the
internal logic, or just to test things out.

.. warning::

   Not part of the stable API.

This module may change without notice. Stick to the top-level :mod:`time_split`-module, or lock down your
dependencies if you need to use the ``support`` module.
"""

from .._backend import DatetimeIndexSplitter, expand_limits, process_available
from .._frontend import default_metrics_formatter, fold_weight, format_expanded_limits, to_string

__all__ = [
    "DatetimeIndexSplitter",
    "default_metrics_formatter",
    "expand_limits",
    "fold_weight",
    "format_expanded_limits",
    "process_available",
    "to_string",
]
