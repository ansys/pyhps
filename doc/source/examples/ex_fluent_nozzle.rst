.. _example_fluent_nozzle:

Fluent nozzle
=============

This example shows how to submit a Fluent nozzle model for solving on Ansys HPC Platform Services. 

.. only:: builder_html

     You can download the :download:`ZIP file <../../../build/fluent_nozzle.zip>` for the
     Fluent nozzle example and use a tool such as 7-Zip to extract the files.

Here is the ``project_setup.py`` script for this example:


.. literalinclude:: ../../../examples/fluent_nozzle/project_setup.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

The example uses an execution script stored server side.