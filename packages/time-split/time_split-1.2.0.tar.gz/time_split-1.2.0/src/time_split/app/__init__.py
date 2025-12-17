"""Supporting functions for the Streamlit companion app.

Run ``pip install time-split[app]`` to install the https://github.com/rsundqvist/time-split-app/, or run
``pip install time-split-app==<version>`` to install the application directly.

.. warning::

   The application API may change without a major version bump.

Once installed, the application will be available under the ``time_split_app`` namespace. Key parts of the API of the
application are documented in the :mod:`.reexport` submodule.

Getting started
---------------
To start the application directly from the command line, run

.. code-block:: bash

   python -m time_split app start

in the terminal. To customize the application, run

.. code-block:: bash

   python -m time_split app new

in the terminal, then modify the ``Dockerfile`` and ``my_extensions.py`` files to suit your needs.
"""

from ._create_explorer_link import create_explorer_link

__all__ = [
    "create_explorer_link",
]
