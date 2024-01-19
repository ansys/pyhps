.. _example_cfx_static_mixer:

CFX static mixer
================

This example shows how to submit a CFX static mixer model for solving on Ansys HPS. 

.. only:: builder_html

     You can download the :download:`ZIP file <../../../build/cfx_static_mixer.zip>` for
     the CFX static mixer example and use a tool such as 7Zip to extract the files.

Here is the ``project_setup.py`` script for this example:

.. literalinclude:: ../../../examples/cfx_static_mixer/project_setup.py
    :language: python
    :caption: project_setup.py

This example uses this ``exec_cfx.py`` execution script instead of a solver command line:

.. literalinclude:: ../../../examples/cfx_static_mixer/exec_cfx.py
    :language: python
    :caption: exec_cfx.py
