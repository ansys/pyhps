.. _example_mapdl_tire_performance:

MAPDL Tire Performance
=======================

This example shows how to submit an MAPDL solver job to REP. The MAPDL model is the Tire-Performance Simulation example included
in the technology demonstration guide (td-57). Solution convergence (gst) and contact status (cnd) tracking files are periodically collected while the job is running. 

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`MAPDL Tire Performance Example <../../../build/mapdl_tyre_performance.zip>`.


.. literalinclude:: ../../../examples/mapdl_tyre_performance/project_setup.py
    :language: python
    :caption: project_setup.py