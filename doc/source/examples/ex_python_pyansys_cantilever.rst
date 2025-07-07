.. _example_python_pyansys_cantilever:

.. note::

    Go to the `bottom of this page`_ to download the ZIP file for the PyAnsys cantilever example.

Running pyAnsys on HPS
======================

This example shows how to run pyAnsys scripts on HPS.

The application simulates a parametrized cantilever by chaining several
pyAnsys packages:

1. Use `pyAnsys Geometry <https://geometry.docs.pyansys.com/>`__ to draw
   a cantilever design
2. Use `pyPrimeMesh <https://prime.docs.pyansys.com/>`__ to apply a
   swept mesh to the cantilever design
3. Use `pyMAPDL <https://mapdl.docs.pyansys.com/>`__ to calculate
   Eigenfrequencies of the cantilever, then display them as output
   parameters

The physical cantilever dimensions, as well as several mesh and
simulation properties are parametrized.

Prerequisites
=============

There are several applications that need to be installed for the example
to function. The precise paths and versions given in the following setup
instructions should be adjusted to the system at hand.

uv
--

The `uv package manager <https://docs.astral.sh/uv/>`__ is used to run
arbitrary python scripts in environments created on the fly. Setup
instructions can be found in the
`python-uv-example <ToBeFilledInWhenBasicExampleMerged>`__.

Ansys Geometry Service
----------------------

The Ansys Geometry Service must be installed for pyAnsys Geometry to
function. Installation instructions can be found
`here <https://geometry.docs.pyansys.com/version/stable/getting_started/faq.html#how-is-the-ansys-geometry-service-installed>`__.
The application should then be registered in the scaler as follows:

================= ===============================
**Property**      **Value**
================= ===============================
Name              Ansys GeometryService
Version           2025 R2
Installation Path /ansys_inc/v252/GeometryService
================= ===============================

With the following environment variables:

=========================== ===============================
**Env Variable**            **Value**
=========================== ===============================
ANSRV_GEO_LICENSE_SERVER    <LICENSE@SERVER>
ANSYS_GEOMETRY_SERVICE_ROOT /ansys_inc/v252/GeometryService
=========================== ===============================

Ansys Prime Server
------------------

The Ansys Prime Server is automatically installed with Ansys 2023 R1 or
later, and is needed for pyPrimeMesh. It should be registered in the
scaler as:

================= ===============================
**Property**      **Value**
================= ===============================
Name              Ansys Prime Server
Version           2025 R2
Installation Path /ansys_inc/v252/GeometryService
================= ===============================

With environment variables:

================ =============================
**Env Variable** **Value**
================ =============================
AWP_ROOT252      /ansys_inc/v252
ANSYS_PRIME_ROOT /ansys_inc/v252/meshing/Prime
================ =============================

Ansys Mechanical APDL
---------------------

Ansys Mechanical APDL is installed with the Ansys unified installer, and
should be auto-detected by the scaler. Two environment variables need to
be added to the application registration for pyMAPDL to work properly:

================== ==================================
**Env Variable**   **Value**
================== ==================================
AWP_ROOT252        /ansys_inc/v252
PYMAPDL_MAPDL_EXEC /ansys_inc/v252/ansys/bin/ansys252
================== ==================================

HPS Python Client
-----------------

To run the example, ``ansys-hps-client`` version 0.11 or higher is
required.

Running the example
===================

To run the example, execute the ``project_setup.py`` script, for example
via ``uv run project_setup.py``. The required packages are
``ansys-hps-client>=0.11`` and ``typer``.

Options
-------

The example supports the following command line arguments:

+--------------------+----------------------------------+----------------------------------+
| **Flag**           | **Example**                      | **Description**                  |
+====================+==================================+==================================+
| -U, --url          | --url=https://localhost:8443/hps | URL of the target HPS instance   |
+--------------------+----------------------------------+----------------------------------+
| -u, --username     | --username=repuser               | Username to log into HPS         |
+--------------------+----------------------------------+----------------------------------+
| -p, --password     | --password=topSecret             | Password to log into HPS         |
+--------------------+----------------------------------+----------------------------------+
| -n, --num-jobs     | --num-jobs=50                    | Number of design points to       |
|                    |                                  | generate                         |
+--------------------+----------------------------------+----------------------------------+
| -m, --num-modes    | --num-modes=3                    | Number of lowest                 |
|                    |                                  | Eigenfrequencies to calculate    |
+--------------------+----------------------------------+----------------------------------+
| -f,                | --target-frequency=100.0         | Frequency [Hz] to target for the |
| --target-frequency |                                  | lowest cantilever mode           |
+--------------------+----------------------------------+----------------------------------+
| -s, --split-tasks  | --split-tasks                    | Split each step into a different |
|                    |                                  | task                             |
+--------------------+----------------------------------+----------------------------------+

Furthermore, it defines the following HPS parameters that are accessible
via the HPS web interface:

+-------------------+-------------------------------------------------------+
| **Parameter**     | **Description**                                       |
+===================+=======================================================+
| canti_length      | Length of the cantilever [um]                         |
+-------------------+-------------------------------------------------------+
| canti_width       | Width of the cantilever [um]                          |
+-------------------+-------------------------------------------------------+
| canti_thickness   | Thickness of the cantilever [um]                      |
+-------------------+-------------------------------------------------------+
| arm_cutoff_width  | By how much should the cantilever arm be thinned [um] |
+-------------------+-------------------------------------------------------+
| arm_cutoff_length | Length of cantilever arm [um]                         |
+-------------------+-------------------------------------------------------+
| arm_slot_width    | Width of the slot cut into the cantilever arm [um]    |
+-------------------+-------------------------------------------------------+
| arm_slot          | Whether there is a slot in the cantilever arm         |
+-------------------+-------------------------------------------------------+
| young_modulus     | Young Modulus of cantilever material [Pa]             |
+-------------------+-------------------------------------------------------+
| density           | Density of cantilever material [kg/m^3]               |
+-------------------+-------------------------------------------------------+
| poisson_ratio     | Poisson ratio of cantilever material                  |
+-------------------+-------------------------------------------------------+
| mesh_swept_layers | Number of layers to generate when sweeping the mesh   |
+-------------------+-------------------------------------------------------+
| num_modes         | Number of lowest lying Eigenfrequencies to calculate  |
+-------------------+-------------------------------------------------------+
| popup_plots       | Whether to show popup plots while running (requires a |
|                   | framebuffer)                                          |
+-------------------+-------------------------------------------------------+
| port_geometry     | Port used by the Ansys GeometryService                |
+-------------------+-------------------------------------------------------+
| port_mesh         | Port used by the Ansys Prime Server                   |
+-------------------+-------------------------------------------------------+
| port_mapdl        | Port used by the Ansys Mechanical APDL service        |
+-------------------+-------------------------------------------------------+
| freq_mode_i       | Frequency of i-th Eigenmode [Hz], iϵ{1,…,num_modes}   |
+-------------------+-------------------------------------------------------+
| clean_venv        | Whether to clean up the (ephemeral) uv venv directory |
|                   | afterwards                                            |
+-------------------+-------------------------------------------------------+

Logic of the example
====================

The example is built up of several files; the logic of this organization
shall be explained in the following.

The script ``project_setup.py`` orchestrates it all. It sets up a HPS
project, uploads files, defines parameters and applies settings. All
communication with HPS is done via this script.

The folder ``exec_scripts`` contains the execution scripts used to run
the tasks. They all have the same basic function: First they write all
HPS parameters to a ``input_parameters.json`` file, then they discover
the available software and run the desired python script using uv, and
finally they fetch parameters that may have been written to
``output_parameters.json`` by the executed python script, and send them
back to the evaluator. There is an execution script ``exec_combined.py``
that is used when all stages are run in a single task, and three more
execution scripts used to split the three stages into different tasks.

The folder ``eval_scripts`` contains the pyAnsys python scripts. There
is one ``eval_combined.py`` script that combines all the functionality
into one monolithic script, and there are three other eval scripts to
split the three stages into three successive tasks. Each of the eval
scripts first reads in the parameters supplied by the execution script
in the ``input_parameters.json`` file, starts a pyAnsys service, and
then runs the pyAnsys program. For more information on the content on
this script, please check the pyAnsys documentation.

Code
====

The files in play for the single task version are the following:

``project_setup.py``:

.. literalinclude:: ../../../examples/python_pyansys_cantilever/project_setup.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

``exec_combined.py``:

.. literalinclude:: ../../../examples/python_pyansys_cantilever/exec_scripts/exec_combined.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

``eval_combined.py``:

.. literalinclude:: ../../../examples/python_pyansys_cantilever/eval_scripts/eval_combined.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

Download the ZIP file for the PyAnsys cantilever example and use
a tool such as 7-Zip to extract the files.

.. _bottom of this page:

.. button-link:: ../_downloads/python_pyansys_cantilever.zip
    :color: black
    :expand:

    Download ZIP file