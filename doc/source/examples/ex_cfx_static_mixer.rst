.. _example_cfx_static_mixer:

CFX static mixer
================

This example shows how to submit a CFX static mixer model to be solved on HPS. 

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`CFX static mixer example <../../../build/cfx_static_mixer.zip>`.

     The project uses an execution script `exec_cfx.py` instead of a solver command line.  

.. literalinclude:: ../../../examples/cfx_static_mixer/project_setup.py
    :language: python
    :caption: project_setup.py

.. literalinclude:: ../../../examples/cfx_static_mixer/exec_cfx.py
    :language: python
    :caption: exec_cfx.py