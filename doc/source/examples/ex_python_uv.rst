.. _example_python_uv:

.. note::

    Go to the `bottom of this page`_ to download the ZIP file for the uv example.

Run arbitrary Python scripts on HPS
===================================

This example shows how to run arbitrary Python scripts. It uses
the `uv <https://docs.astral.sh/uv/>`__ package to generate the required
environments on the fly.

The example sets up a project that plots ``sin(x)`` using NumPy and
Matplotlib and then saves the figure to a file.

The metadata header present in the ``eval.py`` script, which defines the
dependencies, enables uv to take care of the environment setup:

.. code:: python

   # /// script
   # requires-python = "==3.12"
   # dependencies = [
   #     "numpy",
   #     "matplotlib"
   # ]
   # ///

For more information, see `Inline script metadata
<https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata>`__
in the *Python Packaging User Guide* and `Running a script with dependencies <https://docs.astral.sh/uv/guides/scripts/#running-a-script-with-dependencies>`__
in the uv documentation.

Prerequisites
=============

For the example to run, uv must be installed and registered
on the scaler/evaluator. For installation instructions, see
`Installing uv <https://docs.astral.sh/uv/getting-started/installation/>`__
in the uv documentation.

Once uv is installed, the package must be registered in the
scaler/evaluator with the following properties:

.. list-table::
   :header-rows: 1

   * - Property
     - Value
   * - Name
     - uv
   * - Version
     - 0.7.19
   * - Installation Path
     - /path/to/uv
   * - Executable
     - /path/to/uv/bin/uv

Note that the version should be adjusted to the case at hand.

Define a custom cache directory
-------------------------------

The preceding steps set up uv with the cache located in its default location
in the user home directory (~/.cache/uv). Depending on your
situation, you might prefer a different cache location, such as a shared
directory accessible to all evaluators. To define a custom uv
cache directory, add the following environment variable to the
uv package registration in the scaler/evaluator:

.. list-table::
   :header-rows: 1

   * - Environment Variable
     - Value
   * - UV_CACHE_DIR
     - /path/to/custom/uv/cache/dir

Create offline air-gapped setups
--------------------------------

If internet is not available, you can create offline air-gapped setups for uv
using one of these options:

* Pre-populate the uv cache with all desired dependencies.
* Provide a local Python package index and set uv to use it. For
  more information, see
  `Package indexes <https://docs.astral.sh/uv/configuration/indexes/>`__
  in the uv documentation. This index can then sit in a shared location,
  with node-local caching applied.
* Use pre-generated virtual environments. For more information, see
  `uv venv <https://docs.astral.sh/uv/reference/cli/#uv-venv>`__ in the
  uv documentation.

To turn off network access, you can either set the
``UV_OFFLINE`` environment variable or use the ``--offline`` flag with
many uv commands.

Run the example
===============

To run the example, execute the ``project_setup.py`` script::

uv run project_setup.py

This command sets up a project with a number
of jobs. Each job generates a ``plot.png`` file.

Options
-------

The example supports the following command line arguments:

.. list-table::
   :header-rows: 1

   * - Flag
     - Example
     - Description
   * - ``-U``, ``--url``
     - ``--url=https://localhost:8443/hps``
     - URL of the target HPS instance
   * - ``-u``, ``--username``
     - ``--username=repuser``
     - Username to log into HPS
   * - ``-p``, ``--password``
     - ``--password=topSecret``
     - Password to log into HPS
   * - ``-j``, ``--num-jobs``
     - ``--num-jobs=10``
     - Number of jobs to generate

Files
-----

Descriptions follow of the relevant example files.

The project creation script, ``project_setup.py``, handles all communication with the
HPS instance, defines the project, and generates the jobs.

.. literalinclude:: ../../../examples/python_uv/project_setup.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

The script ``eval.py``, which is evaluated on HPS, contains the code to plot a sine and then save 
the figure.

.. literalinclude:: ../../../examples/python_uv/eval.py
    :language: python
    :lines: 23-
    :caption: eval.py

The execution script, ``exec_script.py``, uses uv to run the evaluation script.

.. literalinclude:: ../../../examples/python_uv/exec_script.py
    :language: python
    :lines: 23-
    :caption: exec_script.py

Download the ZIP file for the uv example and use
a tool such as 7-Zip to extract the files.

.. _bottom of this page:

.. button-link:: ../_downloads/python_uv.zip
    :color: black
    :expand:

    Download ZIP file