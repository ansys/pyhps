.. _example_cfx_static_mixer:

CFX Static Mixer
================

This example shows how to submit a CFX Static Mixer model to be solved on REP. 

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`CFX Static Mixer Example <../../../build/cfx_static_mixer.zip>`.

     The project uses an execution script exec_cfx.py instead of a solver command line.  
     The execution script is located in this zip file :download:`Example Execution Scripts <../../../build/exec_scripts.zip>`.

.. literalinclude:: ../../../examples/cfx_static_mixer/project_setup.py
    :language: python
    :caption: project_setup.py

.. literalinclude:: ../../../examples/exec_scripts/exec_cfx.py
    :language: python
    :caption: exec_cfx.py