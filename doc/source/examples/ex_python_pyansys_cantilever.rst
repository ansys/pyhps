.. _example_python_pyansys_cantilever:

.. note::

    Go to the `bottom of this page`_ to download the ZIP file for the PyAnsys cantilever example.

PyAnsys workflow: Cantilever
======================

This example shows how to run PyAnsys scripts on HPS. 
It simulates a cantilever using a chain of several PyAnsys packages:

1. Use `PyAnsys Geometry <https://geometry.docs.pyansys.com/>`__ to draw
   a cantilever design
2. Use `PyPrimeMesh <https://prime.docs.pyansys.com/>`__ to apply a
   swept mesh to the cantilever design
3. Use `PyMAPDL <https://mapdl.docs.pyansys.com/>`__ to calculate
   eigenfrequencies of the cantilever, then display them as output
   parameters

The example parametrizes the physical cantilever dimensions, as well as several mesh and simulation 
properties.

Prerequisites
=============

Several packages need to be installed for the example. 
The paths and versions in the following setup instructions are 
exemplary for an Ansys 2025 R2 installation on a Linux 
system. Be sure to adjust them to your installation.

uv
--

The example uses the `uv package manager <https://docs.astral.sh/uv/>`__ to run
Python scripts. You can find more information, including installation instructions, in the 
:ref:`example_python_uv` example.

Ansys Geometry Service
----------------------

The PyAnsys Geometry package requires Ansys Geometry Service. For installation instructions, see
`How is the Ansys Geometry Service installed? <https://geometry.docs.pyansys.com/version/stable/getting_started/faq.html#how-is-the-ansys-geometry-service-installed>`__ 
in the *Frequently asked questions* of PyAnsys Geometry. 
Once installed, the package must be registered in the scaler/evaluator as follows:

.. list-table::
   :header-rows: 1

   * - Property
     - Value
   * - Name
     - Ansys GeometryService
   * - Version
     - 2025 R2
   * - Installation Path
     - /ansys_inc/v252/GeometryService

With these environment variables:

.. list-table::
   :header-rows: 1

   * - Environment Variable
     - Value
   * - ANSRV_GEO_LICENSE_SERVER
     - <LICENSE@SERVER>
   * - ANSYS_GEOMETRY_SERVICE_ROOT
     - /ansys_inc/v252/GeometryService

Ansys Prime Server
------------------

The PyPrimeMesh package requires Ansys Prime Server, which is automatically installed with Ansys 
2023 R1 or later. Ansys Prime Server must be registered in the scaler/evaluator as follows:

.. list-table::
   :header-rows: 1

   * - Property
     - Value
   * - Name
     - Ansys Prime Server
   * - Version
     - 2025 R2
   * - Installation Path
     - /ansys_inc/v252/meshing/Prime

With these environment variables:

.. list-table::
   :header-rows: 1

   * - Environment Variable
     - Value
   * - AWP_ROOT252   
     - /ansys_inc/v252
   * - ANSYS_PRIME_ROOT 
     - /ansys_inc/v252/meshing/Prime

Ansys Mechanical APDL
---------------------

Ansys Mechanical APDL is installed with the Ansys unified installer. 
The scaler/evaluator automatically detects this package, but two environment variables must 
be added to its registration for PyMAPDL:

.. list-table::
   :header-rows: 1

   * - Environment Variable
     - Value
   * - AWP_ROOT252   
     - /ansys_inc/v252
   * - PYMAPDL_MAPDL_EXEC
     - /ansys_inc/v252/ansys/bin/ansys252

HPS Python Client
-----------------

The example uses unmapped HPS parameters and therefore requires ``ansys-hps-client`` 
version 0.11 or higher.

Run the example
===================

To run the example, execute the ``project_setup.py`` script::

    uv run project_setup.py

This command sets up a project with a number of jobs. 
Each job samples a different cantilever design point.

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
   * - ``-n``, ``--num-jobs``
     - ``--num-jobs=50``
     - Number of design points to generate
   * - ``-m``, ``--num-modes``
     - ``--num-modes=3``
     - Number of lowest eigenfrequencies to calculate
   * - ``-f``, ``--target-frequency``
     - ``--target-frequency=100.0``
     - Frequency in Hertz to target for the lowest cantilever mode
   * - ``-s``, ``--split-tasks``
     - ``--split-tasks``
     - Split each step into a different task

The example defines the following HPS parameters:

.. list-table::
   :header-rows: 1

   * - Parameter
     - Description
   * - canti_length
     - Length of the cantilever [um]
   * - canti_width
     - Width of the cantilever [um]
   * - canti_thickness
     - Thickness of the cantilever [um]
   * - arm_cutoff_width
     - By how much should the cantilever arm be thinned [um]
   * - arm_cutoff_length
     - Length of the cantilever arm [um]
   * - arm_slot_width
     - Width of the slot cut into the cantilever arm [um]
   * - arm_slot
     - Whether there is a slot in the cantilever arm
   * - young_modulus
     - Young Modulus of the cantilever material [Pa]
   * - density
     - Density of the cantilever material [kg/m^3]
   * - poisson_ratio
     - Poisson ratio of the cantilever material
   * - mesh_swept_layers
     - Number of layers to generate when sweeping the mesh
   * - num_modes
     - Number of eigenfrequencies to calculate
   * - popup_plots
     - Whether to show popup plots (requires a framebuffer)
   * - port_geometry
     - Port used by Ansys GeometryService
   * - port_mesh
     - Port used by Ansys Prime Server
   * - port_mapdl
     - Port used by the Ansys Mechanical APDL service
   * - freq_mode_i
     - Frequency of i-th eigenmode [Hz], iϵ{1,…,num_modes}
   * - clean_venv
     - Whether to delete the venvs after execution

Logic of the example
====================

The example comprises several files. Their roles are as follows:

The script ``project_setup.py`` handles all communication with the HPS instance. 
It sets up a project, uploads files, defines parameters, and applies settings.

The folder ``exec_scripts`` contains the execution scripts that start
the evaluation scripts. Each of them first writes all
HPS parameters to an ``input_parameters.json`` file, discovers
the available software, and then runs the corresponding evaluation script with uv. 
Finally each execution script fetches parameters that may have been written to
``output_parameters.json`` by the evaluation script and sends them
back to the evaluator. Optionally, the execution scripts clean up the ephemeral venvs
created by uv. 
The execution script ``exec_combined.py`` runs all steps in a single task, the other three
execution scripts split the three steps into individual tasks.

The folder ``eval_scripts`` contains the PyAnsys evaluation scripts.  
Each of the evaluation scripts first reads in the parameters supplied by the execution script
in the ``input_parameters.json`` file, then starts a PyAnsys service, and
finally runs the PyAnsys program. 
The script ``eval_combined.py`` combines all stages in one monolithic task, 
the other three evaluation scripts split the three stages into three successive tasks.
You can find more information on the content of these scripts in the 
`User guide <https://docs.pyansys.com/version/dev/user_guide.html>`__ 
of the *PyAnsys project*.



Code
====

The files relevant for the single task version follow.

The project creation script ``project_setup.py``:

.. literalinclude:: ../../../examples/python_pyansys_cantilever/project_setup.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

The combined execution script ``exec_combined.py``:

.. literalinclude:: ../../../examples/python_pyansys_cantilever/exec_scripts/exec_combined.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

The combined evaluation script ``eval_combined.py``:

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