.. _examples:

Examples
========

The examples in this section show how to interact with a REP server in Python using
PyHPS. Each example consists of a Python script plus a data file, such as a solver input file. 
You can execute many Python scripts with these command-line arguments:

* ``-n``, ``--name``: Name of the REP project
* ``-U``, ``--url``: URL or the REP server (default: https://localhost:8443/rep)
* ``-u``, ``--username``: REP username (default: repadmin)
* ``-p``, ``--password``: REP password (default: repadmin)
* ``-v``, ``--ansys-version``: Ansys version (default: |ansys_version|)

A link to download the required resources is available on each example page. If
desired, you can download the required resources for all examples by downloading
one :download:`ZIP file <../../../build/pyhps_examples.zip>`.

.. toctree::
  :hidden:
  :maxdepth: 3

  ex_motorbike_frame
  ex_motorbike_frame_query
  ex_mapdl_tire_performance
  ex_mapdl_linked_analyses
  ex_lsdyna_job
  ex_fluent_2d_heat_exchanger
  ex_fluent_nozzle
  ex_cfx_static_mixer
  ex_python_two_bar

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - :ref:`example_mapdl_motorbike_frame`
     - Create from scratch a REP project consisting of an Ansys APDL beam model of a tubular steel trellis motorbike frame. This example shows how to create a parameter study and submit design points.
   * - :ref:`example_mapdl_motorbike_frame_query`
     - Query an existing project and download output files.
   * - :ref:`example_mapdl_tire_performance`
     - Submit an MAPDL analysis as a single job. Solution convergence and contact tracking files are periodically collected. 
   * - :ref:`example_mapdl_linked_analyses`
     - Submit an MAPDL linked analysis workflow as a multi-task job to the REP server.
   * - :ref:`example_lsdyna_job`
     - Submit, monitor, and download results of an LS-DYNA job. 
   * - :ref:`example_fluent_2d_heat_exchanger`
     - Submit a Fluent solve job to the REP server.
   * - :ref:`example_fluent_nozzle`
     - Submit a Fluent solve job to the REP server using an execution script.
   * - :ref:`example_cfx_static_mixer`
     - Submit a CFX solve job to the REP server using an execution script.
   * - :ref:`example_python_two_bar`
     - Create a REP project that solves a two-bar truss problem with Python.
