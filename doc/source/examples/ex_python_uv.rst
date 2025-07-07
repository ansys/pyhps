.. _example_python_uv:

.. note::

    Go to the `bottom of this page`_ to download the ZIP file for the two-bar truss example.

Running arbitrary python scripts on HPS
=======================================

This example shows how arbitrary python scripts can be run on HPS, by
using `uv <https://docs.astral.sh/uv/>`__ to generate the required
environments on the fly.

The example sets up a project that shall plot ``sin(x)`` using numpy and
matplotlib, and then save the figure to a file.

The main feature enabling uv to take care of the environment setup is
the metadata header present in the ``eval.py`` script, which defines the
dependencies:

.. code:: python

   # /// script
   # requires-python = "==3.12"
   # dependencies = [
   #     "numpy",
   #     "matplotlib"
   # ]
   # ///

More information can be found `here
(python.org) <https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata>`__
and `here
(astral.sh) <https://docs.astral.sh/uv/guides/scripts/#running-a-script-with-dependencies>`__.

Prerequisites
=============

In order for the example to run, ``uv`` must be installed and registered
on the scaler/evaluator. Installation instructions can be found
`here <https://docs.astral.sh/uv/getting-started/installation/>`__.

Once uv is installed, the application must be registered in the
scaler/evaluator with the following properties:

================= ==================
**Property**      **Value**
================= ==================
Name              uv
Version           0.6.14
Installation Path /path/to/uv
Executable        /path/to/uv/bin/uv
================= ==================

Note that the version should be adjusted to the case at hand.

Custom cache directory
----------------------

The preceding steps setup uv with the cache located in its default location
in the user home directory (~/.cache/uv). Depending on the individual
situation, other cache locations may be preferred, such as a shared
directory accessible to all evaluators. In order to define a custom uv
cache directory, the following environment variable can be added to the
uv application registration in the scaler/evaluator:

================ ============================
**Environment Variable** **Value**
================ ============================
UV_CACHE_DIR     /path/to/custom/uv/cache/dir
================ ============================

Air-gapped setups
----------------

For air-gapped setups where no internet connectivity is available, there
are several options for a successful uv setup:

1. Pre-populate the uv cache with all desired dependencies.
2. Provide a local python package index, and set uv to use it. More
   information can be found
   `here <https://docs.astral.sh/uv/configuration/indexes/>`__. This
   index could then sit in a shared location, with node-local caching
   applied.
3. Use pre-generated virtual environments, see
   `here <https://docs.astral.sh/uv/reference/cli/#uv-venv>`__

In order to turn off network access, one can either set the
``UV_OFFLINE`` environment variable, or use the ``--offline`` flag with
many uv commands.

Running the example
===================

To run the example, execute the ``project_setup.py`` script, for example
via ``uv run project_setup.py``. This sets up a project with a number
of jobs, and each job shall generate a ``plot.png`` file.

Options
-------

The example supports the following command line arguments:

+--------------+---------------------------------+----------------------------------+
| **Flag**     | **Example**                     | **Description**                  |
+==============+=================================+==================================+
| -U, –url     | –url=https://localhost:8443/hps | URL of the target HPS instance   |
+--------------+---------------------------------+----------------------------------+
| -u,          | –username=repuser               | Username to log into HPS         |
| –username    |                                 |                                  |
+--------------+---------------------------------+----------------------------------+
| -p,          | –password=topSecret             | Password to log into HPS         |
| –password    |                                 |                                  |
+--------------+---------------------------------+----------------------------------+
| -j,          | –num-jobs=10                    | Number of jobs to generate       |
| –num-jobs    |                                 |                                  |
+--------------+---------------------------------+----------------------------------+

Files
-----

The relevant files of the example are:

``project_setup.py``: Handles all communication with the HPS instance.
  Defines the project and generates the jobs.

.. literalinclude:: ../../../examples/python_uv/project_setup.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

``eval.py``: The script that is evaluated on HPS. Contains the code to
  plot a sine, and then save the figure.

.. literalinclude:: ../../../examples/python_uv/eval.py
    :language: python
    :lines: 23-
    :caption: eval.py

``exec_script.py``: Execution script that uses uv to run the
  evaluation script.

.. literalinclude:: ../../../examples/python_uv/exec_script.py
    :language: python
    :lines: 23-
    :caption: exec_script.py