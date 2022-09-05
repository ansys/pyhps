.. _examples:

Examples
========

Here you can find some examples showing how to interact with a REP server in Python using the ``ansys-rep-client``. 
Examples consist of a Python script plus some data files (e.g. solver input files). 
Many of the Python scripts can be executed with the following command line arguments:

* ``-n``, ``--name``: name of the REP project
* ``-U``, ``--url``: url or the REP server (default: https://localhost:8443/rep)
* ``-u``, ``--username``: REP username (default: repadmin)
* ``-p``, ``--password``: REP password (default: repadmin)

A link to download all the required resources is available at each example page. 

You can also download the entire set of examples :download:`Download All Examples <../../../build/pyrep_examples.zip>`.

.. toctree::
  :hidden:
  :maxdepth: 3

  ex_motorbike_frame
  ex_motorbike_frame_query
  ex_mapdl_tire_performance
  ex_mapdl_linked_analyses
  ex_lsdyna_job
  ex_python_two_bar

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - :ref:`example_mapdl_motorbike_frame`
     - Create from scratch a REP project consisting of an Ansys APDL beam model of a tubular steel trellis motorbike-frame. This example shows how to create a parameter study and submit design points.
   * - :ref:`example_mapdl_motorbike_frame_query`
     - Query an existing project and download output files.
   * - :ref:`example_mapdl_tire_performance`
     - Submit an MAPDL analysis as a single job. Solution convergence and contacts tracking files are periodically collected. 
   * - :ref:`example_mapdl_linked_analyses`
     - Submit an MAPDL linked analysis workflow as a multi-task job to REP.
   * - :ref:`example_lsdyna_job`
     - Submit, monitor and download results of an LS-DYNA job. 
   * - :ref:`example_python_two_bar`
     - Create a REP project solving a Two-Bar Truss problem with Python.