from base64 import b16encode as encode_binary_data
from datetime import datetime
from typing import Any, Unpack
from urllib.parse import ParseResult, urlencode, urlparse, urlunparse

from .._backend import DatetimeIndexSplitter
from .._docstrings import docs
from ..types import DatetimeIndexSplitterKwargs, DatetimeIterable


@docs
def create_explorer_link(
    host: str,
    data: DatetimeIterable | str | bytes | None = None,
    available: DatetimeIterable | str | bytes | None = None,
    *,
    show_removed: bool = True,
    skip_default: bool = False,
    **kwargs: Unpack[DatetimeIndexSplitterKwargs],
) -> str:
    """Create an application URL.

    Args:
        host: Base address where the application is hosted.
        data: {available} Regular `available` arguments (as passed to e.g. :func:`time_split.split`) are encoded as
            a date range to generate dummy data for.
            Pass a ``str`` to use a bundled dataset, or ``bytes`` to use a custom loader. Note that this will disable
            verification of the `**kwargs`.
        available: Alias of `data`.
        skip_default: If ``True``, do not include default split params in the link.
        show_removed: {show_removed}
        kwargs: Keyword arguments for the :func:`time_split.split`-function.

    Returns:
        An encoded URL.

    Examples:
        Getting the URL for a local host.

        >>> create_explorer_link(
        ...     host="http://localhost:8501",
        ...     available=("2019-04-11 00:35:00", "2019-05-11 21:30:00"),
        ...     schedule="0 0 * * MON,FRI",
        ... )
        'http://localhost:8501?data=1554942900-1557610200&schedule=0+0+%2A+%2A+MON%2CFRI&show_removed=True'

        To start the application using locally using |image| Docker, run

        .. code-block:: bash

           docker run -p 8501:8501 rsundqvist/time-split

        in the terminal.

        .. |image| image:: https://img.shields.io/docker/image-size/rsundqvist/time-split/latest?logo=docker&label=time-split
                   :target: https://hub.docker.com/r/rsundqvist/time-split/
                   :alt: Docker Image Size (tag)
    """
    if data is None:
        if available is None:
            raise ValueError("Exactly one of `data` and `available` must be given.")
        data = available
    elif data is not None and available is not None:
        raise ValueError("Exactly one of `data` and `available` must be given.")

    pr = _create_explorer_link(host, data, show_removed=show_removed, skip_default=skip_default, **kwargs)
    return urlunparse(pr)


def _create_explorer_link(
    host: str,
    data: DatetimeIterable | str | bytes,
    *,
    show_removed: bool = True,
    skip_default: bool = False,
    **kwargs: Unpack[DatetimeIndexSplitterKwargs],
) -> ParseResult:
    query = _create_query(data, skip_default=skip_default, show_removed=show_removed, kwargs=kwargs)

    pr: ParseResult = urlparse(host)  # scheme netloc path params query fragment
    if pr.query:
        raise ValueError(f"Bad {host=}; query={pr.query!r} is not allowed.")
    return pr._replace(query=urlencode(query))


def _create_query(
    data: DatetimeIterable | str | bytes,
    *,
    skip_default: bool,
    show_removed: bool,
    kwargs: DatetimeIndexSplitterKwargs,
) -> dict[str, Any]:
    query: dict[str, Any] = {}

    if isinstance(data, bytes):
        data = "0x" + encode_binary_data(data).decode()

    if isinstance(data, str):
        query = {"data": data, **kwargs}
    else:
        splitter = DatetimeIndexSplitter(**kwargs)
        start, end = splitter._materialize_schedule(data).available_metadata.limits
        query["data"] = _get_data_param(start, end)

        if skip_default:
            schedule = kwargs["schedule"]
            query["schedule"] = schedule

            default = DatetimeIndexSplitter(schedule).as_dict()
            no_defaults = {
                key: value
                for key, value in kwargs.items()
                if value != default[key]  # type: ignore[literal-required]
            }
            query.update(no_defaults)
        else:
            query.update(kwargs)

    query["show_removed"] = show_removed
    return query


def _get_data_param(start: datetime, end: datetime) -> str:
    return f"{int(start.timestamp())}-{int(end.timestamp())}"
