# Time Split  <!-- omit in toc -->
Time-based k-fold validation splits for heterogeneous data.

-----------------
[![PyPI - Version](https://img.shields.io/pypi/v/time-split.svg)](https://pypi.python.org/pypi/time-split)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/time-split.svg)](https://pypi.python.org/pypi/time-split)
[![Tests](https://github.com/rsundqvist/time-split/workflows/tests/badge.svg)](https://github.com/rsundqvist/time-split/actions?workflow=tests)
[![Codecov](https://codecov.io/gh/rsundqvist/time-split/branch/master/graph/badge.svg)](https://codecov.io/gh/rsundqvist/time-split)
[![Read the Docs](https://readthedocs.org/projects/time-split/badge/)](https://time-split.readthedocs.io/)
[![PyPI - License](https://img.shields.io/pypi/l/time-split.svg)](https://pypi.python.org/pypi/time-split)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/rsundqvist/time-split/latest?logo=docker&label=time-split)](https://hub.docker.com/r/rsundqvist/time-split/)

<div align="center">
  <img alt="Plotted folds on a two-by-two grid." 
       title="Examples" height="300" width="1200" 
  src="https://raw.githubusercontent.com/rsundqvist/time-split/master/docs/2x2-examples.jpg"><br>
</div>

Folds plotted on a two-by-two grid. See the
[examples](https://time-split.readthedocs.io/en/stable/auto_examples/index.html) page for more.

## What is it?
A library for creating time-based cross-validation splits of _heterogeneous_ data, such as raw transaction data with 
strong non-stationary characteristics.

## Highlighted Features
- [Splitting schedules](https://time-split.readthedocs.io/en/stable/guide/schedules.html) based on a fixed interval, 
  a CRON-expression, or a pre-defined list.
- [Data selection](https://time-split.readthedocs.io/en/stable/guide/spans.html) based on a timedelta, or the splitting 
  schedule itself.
- Automatically extract and [normalize](https://time-split.readthedocs.io/en/stable/guide/expand-limits.html) data limits for 
  supported data types.
- [Plotting function](https://time-split.readthedocs.io/en/stable/api/time_split.html#time_split.plot) for
  visualization of folds. Display fold sizes (hour/row count), or 
  [use custom text](https://time-split.readthedocs.io/en/stable/auto_examples/plotting_with_metrics.html).
- [Integrations](https://time-split.readthedocs.io/en/stable/api/time_split.integration.html) for popular 
  libraries such as `pandas`, `polars` and `scikit-learn`.
- Convenient [web application](#experimenting-with-parameters) for exploring folds with different parameters.

## Experimenting with parameters
The **Time Split** application
(available [here](https://time-split.streamlit.app/?data=1554942900-1557610200&schedule=0+0+%2A+%2A+MON%2CFRI&n_splits=2&step=2&show_removed=True))
is designed to help evaluate the effects of different
[parameters](https://time-split.readthedocs.io/en/stable/#parameter-overview).
To start it locally, run
```sh
docker run -p 8501:8501 rsundqvist/time-split
```
or 
```bash
pip install time-split[app]
python -m time_split app start
```
in the terminal. You may use
[`create_explorer_link()`](https://time-split.readthedocs.io/en/stable/api/time_split.app.html#time_split.app.create_explorer_link)
to build application URLs with preselected splitting parameters.

Click [here](https://time-split.readthedocs.io/en/stable/api/time_split.app.reexport.html) for documentation of the most
important types, functions and classes used by the application.

## Installation
The package is published through the [Python Package Index (PyPI)]. Source code
is available on GitHub: https://github.com/rsundqvist/time-split

```sh
pip install -U time-split
```

This is the preferred method to install ``time-split``, as it will always install the
most recent stable release.

## License
[MIT](LICENSE.md)

## Documentation
Hosted on Read the Docs: https://time-split.readthedocs.io

## Contributing

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome. To get 
started, see the [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

[Python Package Index (PyPI)]: https://pypi.org/project/time-split
