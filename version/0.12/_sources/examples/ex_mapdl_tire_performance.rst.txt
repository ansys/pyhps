.. _example_mapdl_tire_performance:

.. note::

    Go to the `bottom of this page`_ to download the ZIP file for the MAPDL tire performance example.

MAPDL tire performance
=======================

This example shows how to submit an MAPDL solver job to HPS. The MAPDL model is the tire
performance simulation example included in the technology demonstration guide (td-57).
Solution convergence (GST) and contact status (CND) tracking files are periodically collected
while the job is running. 

Here is the ``project_setup.py`` file for this project:

.. literalinclude:: ../../../examples/mapdl_tyre_performance/project_setup.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

Download the ZIP file for the MAPDL tire performance example and use
a tool such as 7-Zip to extract the files.

.. _bottom of this page:

.. button-link:: ../_downloads/mapdl_tyre_performance.zip
    :color: black
    :expand:

    Download ZIP file