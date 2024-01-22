.. _example_fluent_nozzle:

Fluent Nozzle
=============

This example shows how to submit a Fluent nozzle model for solving on REP. 

.. only:: builder_html

     You can download the :download:`ZIP file <../../../build/fluent_nozzle.zip>` for the
     Fluent nozzle example and use a tool such as 7-Zip to extract the files.

Here is the ``project_setup.py`` script for this example:


.. literalinclude:: ../../../examples/fluent_nozzle/project_setup.py
    :language: python
    :caption: project_setup.py

The example uses an ``exec_fluent.py`` execution script instead of a solver command line.  

.. literalinclude:: ../../../examples/fluent_nozzle/exec_fluent.py
    :language: python
    :caption: exec_fluent.py
