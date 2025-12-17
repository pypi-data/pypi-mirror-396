import logging
from collections.abc import Callable, Iterator, MutableMapping, Sequence
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Generic, overload

import pandas as pd
from rics.collections.dicts import flatten_dict
from rics.strings import format_seconds as fmt_sec

from ..settings import log_split_progress as settings
from ..types import (
    DatetimeSplitBounds,
    FormatMetrics,
    GetMetrics,
    LogSplitProgress,
    LogSplitProgressLoggerArg,
    MetricsType,
    SplitProgressExtras,
)
from ._to_string import _PrettyTimestamp


def log_split_progress(
    splits: Sequence[DatetimeSplitBounds],
    *,
    logger: LogSplitProgressLoggerArg = "time_split",
    start_level: int = logging.INFO,
    end_level: int = logging.INFO,
    extra: dict[str, Any] | None = None,
    get_metrics: GetMetrics[MetricsType] | None = None,
) -> LogSplitProgress:
    """Log iteration progress.

    Args:
        splits: Splits to iterate over.
        logger: Logger or logger name to use.
        start_level: Log level to use for the :attr:`fold-begin message <.settings.log_split_progress.START_MESSAGE>`.
        end_level: Log level to use for the :attr:`fold-end message <.settings.log_split_progress.END_MESSAGE>`.
        extra: Immutable, user-defined `extra`-arguments to use when logging, merged with progress-related extras (see
            :class:`~time_split.types.SplitProgressExtras`).
        get_metrics: A callable ``(training_date) -> fold_metrics | str`` (see :attr:`~.DatetimeSplit.training_date`).
            If given, metrics are added to the :attr:`fold-end message <.settings.log_split_progress.END_MESSAGE>`. The
            message is formatted using the :func:`default formatter <.support.default_metrics_formatter>` unless
            :attr:`~.settings.log_split_progress.FORMAT_METRICS` is set. If this callback returns a ``str`` argument,
            the :func:`default formatter <.support.default_metrics_formatter>` will assume that the metrics are
            pre-formatted, simply appending the formatted metrics to the
            :attr:`fold-end message <.settings.log_split_progress.END_MESSAGE>` as-is.

    Returns:
        A :class:`.LogSplitProgress` object.

    Examples:
        Configuring the `logger` name and
        :attr:`fold-begin message <.settings.log_split_progress.START_MESSAGE>` log level.

        >>> from time_split import split, log_split_progress
        >>> schedule = ["2023-08-16", "2023-08-17 12", "2023-08-19"]
        >>> tracked_splits = log_split_progress(
        ...     split(schedule),
        ...     logger="progress",
        ...     start_level=logging.DEBUG,
        ... )
        >>> list(splits)  # doctest: +SKIP
        [progress:DEBUG] Begin fold 1/2: '2023-08-09' <= [schedule: '2023-08-16' (Wednesday)] < '2023-08-17 12:00:00'.
        [progress:INFO] Finished fold 1/2 [schedule: '2023-08-16' (Wednesday)] after 5m 18s.
        [progress:DEBUG] Begin fold 2/2: '2023-08-10 12:00:00' <= [schedule: '2023-08-17 12:00:00' (Thursday)] < '2023-08-19'.
        [progress:INFO] Finished fold 2/2 [schedule: '2023-08-17 12:00:00' (Thursday)] after 4m 3s.

        Using the `get_metrics` callback argument.

        >>> metrics = {
        ...     "2023-08-16 00:00:00": {"rmse": {"train": 0.11, "test": 0.5}},
        ...     "2023-08-17 12:00:00": {"rmse": {"test": 0.5, "future": 20.19}},
        ... }
        >>> tracked_splits = log_split_progress(
        ...     split(schedule),
        ...     get_metrics=lambda key: metrics[str(key)],
        ... )
        >>> list(tracked_splits)  # doctest: +SKIP
        [time_split:INFO] Begin fold 1/2: '2023-08-09' <= [schedule: '2023-08-16' (Wednesday)] < '2023-08-17 12:00:00'.
        [time_split:INFO] Finished fold 1/2 [schedule: '2023-08-16' (Wednesday)] after 5m 18s. Fold metrics:
        rmse.train   0.11
        rmse.test     0.5
        [time_split:INFO] Begin fold 2/2: '2023-08-10 12:00:00' <= [schedule: '2023-08-17 12:00:00' (Thursday)] < '2023-08-19'.
        [time_split:INFO] Finished fold 2/2 [schedule: '2023-08-17 12:00:00' (Thursday)] after 4m 3s. Fold metrics:
        rmse.test       0.5
        rmse.future   20.19

        Formatting was done using the :func:`default formatter <.support.default_metrics_formatter>`, since the
        :attr:`~.settings.log_split_progress.FORMAT_METRICS` setting is ``None``.

    """
    logger = logging.getLogger(logger) if isinstance(logger, str) else logger

    if isinstance(logger, logging.LoggerAdapter) and not hasattr(logger, "merge_extra"):
        # Backport of https://github.com/python/cpython/pull/107292
        logger = _MergingLoggerAdapter(logger.logger, logger.extra)

    return _ProgressTracker(
        splits,
        logger=logger,
        fold_format=settings.FOLD_FORMAT,
        start_level=start_level,
        start_message=settings.START_MESSAGE,
        end_level=end_level,
        end_message=settings.END_MESSAGE,
        seconds_formatter=settings.SECONDS_FORMATTER or fmt_sec,
        user_extra={} if extra is None else extra.copy(),  # Not actually immutable; deepcopy can be very expensive.
        get_metrics=get_metrics,
        format_metrics=settings.FORMAT_METRICS or default_metrics_formatter,
    )


@dataclass(frozen=True)
class _ProgressTracker(LogSplitProgress, Generic[MetricsType]):
    splits: Sequence[DatetimeSplitBounds]
    logger: logging.Logger | logging.LoggerAdapter  # type: ignore[type-arg]
    fold_format: str
    start_level: int
    start_message: str
    end_level: int
    end_message: str
    seconds_formatter: Callable[[float], str]
    user_extra: dict[str, Any]
    get_metrics: GetMetrics[MetricsType] | None
    format_metrics: FormatMetrics[MetricsType]

    @overload
    def __getitem__(self, index: int) -> DatetimeSplitBounds: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[DatetimeSplitBounds]: ...

    def __getitem__(self, index: int | slice) -> DatetimeSplitBounds | Sequence[DatetimeSplitBounds]:
        return self.splits[index]

    def __len__(self) -> int:
        return len(self.splits)

    def __iter__(self) -> Iterator[DatetimeSplitBounds]:
        for n, split in enumerate(self.splits, start=1):
            default_extras = SplitProgressExtras[MetricsType](
                n=n,
                n_splits=len(self.splits),
                start=split.start.isoformat(),
                mid=split.mid.isoformat(),
                end=split.end.isoformat(),
            )
            extra = {**self.user_extra, **default_extras}
            kwargs: dict[str, Any] = dict(
                n=n,
                n_splits=len(self.splits),
                start=_PrettyTimestamp(split.start),
                mid=_PrettyTimestamp(split.mid),
                end=_PrettyTimestamp(split.end),
                **self.user_extra,
            )
            kwargs.update(fold=self.fold_format.format(**kwargs))

            self.logger.log(self.start_level, self.start_message.format(**kwargs), extra=extra)

            # Yield split and count user time.
            start = perf_counter()
            yield split
            seconds = round(perf_counter() - start, 6)

            kwargs.update(
                seconds=seconds,
                formatted_seconds=self.seconds_formatter(seconds),
            )
            msg = self.end_message.format(**kwargs)

            if self.get_metrics is not None:
                extra["metrics"] = self.get_metrics(split.mid)
                msg = self.format_metrics(msg, extra["metrics"])

            extra.update(seconds=seconds)
            self.logger.log(self.end_level, msg, extra=extra)


def default_metrics_formatter(end_message: str, metrics: dict[Any, Any] | pd.Series | pd.DataFrame | str | Any) -> str:
    """Default formatting implementation.

    Format using an appropriate pandas ``to_string()``-method if `metrics` is a ``dict`` or a pandas type. Nested
    dictionaries are flattened using :func:`~rics.collections.dicts.flatten_dict` if `metrics` is a dict-of-dicts.

    Metrics of type ``str`` are assumed to be preformatted, and are appended to `end_message` as-is.

    If any other types are given, fall back to
    ``f"{end_message} Metrics: {metrics}"``.

    Examples:
        Formatting a nested dict.

        >>> metrics = {"rmse": {"train": 0.11, "test": 0.5, "future": 20.19}}

        >>> print(default_metrics_formatter("End message.", metrics))
        End message. Fold metrics:
              train  test  future
        rmse   0.11   0.5   20.19

        Formatting a :class:`pandas.DataFrame`.

        >>> metrics = {"me": [0.1, 0.2, 0.3], "rmse": [0.11, 0.5, 20.19]}
        >>> df = pd.DataFrame(metrics, index=["train", "test", "future"])
        >>> print(default_metrics_formatter("End message.", df))
        End message. Fold metrics:
                 me   rmse
        train   0.1   0.11
        test    0.2   0.50
        future  0.3  20.19

        The index printed  unless` it is a :class:`pandas.RangeIndex`.
    """
    if isinstance(metrics, dict):
        metrics = _convert_dict(metrics)

    if isinstance(metrics, (pd.Series, pd.DataFrame)):
        if isinstance(metrics, pd.DataFrame):
            with_index = not isinstance(metrics, pd.RangeIndex)
        else:
            with_index = True
        return f"{end_message} Fold metrics:\n{metrics.round(3).to_string(index=with_index)}"
    elif isinstance(metrics, str):
        return f"{end_message} {metrics}"
    else:
        return f"{end_message} Metrics: {metrics}"


class _MergingLoggerAdapter(logging.LoggerAdapter[Any]):
    # TODO(3.13): Use merge_extra=True init arg
    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> tuple[Any, MutableMapping[str, Any]]:
        """See https://github.com/python/cpython/pull/107292."""
        kwargs["extra"] = {**self.extra, **kwargs["extra"]} if "extra" in kwargs and self.extra else self.extra
        return msg, kwargs


def _convert_dict(metrics: dict[Any, Any]) -> dict[Any, Any] | pd.DataFrame | pd.Series:
    original = metrics

    scalar_leaves: bool = False

    if all(isinstance(v, dict) for v in metrics.values()):
        flat = flatten_dict(metrics)

        # A single dot usually indicates nesting one level deep; can be formatted as a DataFrame.
        if any(k.count(".") != 1 for k in flat) and all(pd.api.types.is_scalar(v) for v in flat.values()):
            metrics = flat
    elif all(pd.api.types.is_scalar(v) for v in original.values()):
        scalar_leaves = True

    try:
        if scalar_leaves:
            return pd.Series(metrics)

        df = pd.DataFrame(metrics)
    except Exception:
        return original

    if len(df) > len(df.columns):
        df = df.T  # Prefer wider horizontal output
    return df
