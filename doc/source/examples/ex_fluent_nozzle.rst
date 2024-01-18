.. _example_fluent_nozzle:

Fluent nozzle
=============

This example shows how to submit a Fluent nozzle model to be solved on REP. 

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`Fluent Nozzle Example <../../../build/fluent_nozzle.zip>`.

     The project uses an execution script `exec_fluent.py` instead of a solver command line.  

.. literalinclude:: ../../../examples/fluent_nozzle/project_setup.py
    :language: python
    :caption: project_setup.py

.. literalinclude:: ../../../examples/fluent_nozzle/exec_fluent.py
    :language: python
    :caption: exec_fluent.py