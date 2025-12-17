"""Reexported members of the ``time_split_app`` namespace.

.. warning::

   The application API may change without a major version bump.

See :mod:`time_split_app.config` for  variable-based configuration options.
"""

from time_split_app.datasets import Dataset, DatasetConfig, DuplicateIndexError, load_dataset, load_dataset_configs
from time_split_app.widgets import DataLoaderWidget, DurationWidget, select_datetime, select_duration
from time_split_app.widgets import types as _types
from time_split_app.widgets.types import QueryParams

SelectSplitParams = _types.SelectSplitParams
"""Type of :attr:`~time_split_app.config.SPLIT_SELECT_FN`.

See Also:
    * :func:`time_split.split`
    * :attr:`~time_split.types.DatetimeIndexSplitterKwargs`.
"""
PlotFn = _types.PlotFn
"""Type of :attr:`~time_split_app.config.PLOT_FN`."""
LinkFn = _types.LinkFn
"""Type of :attr:`~time_split_app.config.LINK_FN`."""

__all__ = [
    "DataLoaderWidget",
    "Dataset",
    "DatasetConfig",
    "DuplicateIndexError",
    "DurationWidget",
    "LinkFn",
    "PlotFn",
    "QueryParams",
    "SelectSplitParams",
    "load_dataset",
    "load_dataset_configs",
    "select_datetime",
    "select_duration",
]
