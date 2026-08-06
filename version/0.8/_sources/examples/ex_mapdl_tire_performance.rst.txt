.. _example_mapdl_tire_performance:

MAPDL tire performance
=======================

This example shows how to submit an MAPDL solver job to HPS. The MAPDL model is the tire
performance simulation example included in the technology demonstration guide (td-57).
Solution convergence (GST) and contact status (CND) tracking files are periodically collected
while the job is running. 

.. only:: builder_html

     You can download the :download:`ZIP file <../../../build/mapdl_tyre_performance.zip>`
     for the MAPDL tire performance example and use a tool such as 7-Zip to extract the files.

Here is the ``project_setup.py`` file for this project:

.. literalinclude:: ../../../examples/mapdl_tyre_performance/project_setup.py
    :language: python
    :lines: 23-
    :caption: project_setup.py
