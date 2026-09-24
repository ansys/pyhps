.. _example_hps_mini:

Connect to hps-mini
===================

This example shows how to discover a local hps-mini executable and create a
PyHPS client connected to it.

Configure discovery
-------------------

PyHPS searches for ``hps-mini.exe`` on Windows and ``hps-mini`` on other
platforms. It checks the current directory, the ``binaries`` directory, and the
system ``PATH``.

To use an executable in another location, set ``HPS_MINI_PATH`` before running
your Python application.

On Windows PowerShell::

    $env:HPS_MINI_PATH = "D:\AnsysDev\hps-local\hps-mini.exe"

On Linux or macOS::

    export HPS_MINI_PATH=/path/to/hps-mini

You can optionally set ``HPS_MINI_DATA_DIR`` to select the directory where
hps-mini stores its local state.

Create a client
---------------

Use :func:`ansys.hps.client.create_mini_client` to discover hps-mini, obtain its
connection details, and create a configured client:

.. code-block:: python

    from ansys.hps.client import create_mini_client

    client = create_mini_client()
    print(client.url)

You can also supply the executable directly instead of setting an environment
variable:

.. code-block:: python

    from ansys.hps.client import create_mini_client

    client = create_mini_client(executable=r"D:\AnsysDev\hps-local\hps-mini.exe")

Inspect discovery and status
----------------------------

Use :func:`ansys.hps.client.find_hps_mini` to inspect the discovered executable
and :func:`ansys.hps.client.get_hps_mini_status` to inspect the running local
instance:

.. code-block:: python

    from ansys.hps.client import find_hps_mini, get_hps_mini_status

    executable = find_hps_mini()
    status = get_hps_mini_status()

    print(f"Executable: {executable}")
    print(f"URL: {status.url}")
    print(f"PID: {status.pid}")

The returned :class:`ansys.hps.client.HpsMiniStatus` also contains the API key
used by :func:`ansys.hps.client.create_mini_client`. Avoid printing or storing
that key in logs.
