.. _example_cfx_static_mixer:

.. note::

    Go to the `bottom of this page`_ to download the ZIP file for the CFX static mixer example.

CFX static mixer
================

This example shows how to submit a CFX static mixer model for solving on Ansys HPS. 

Here is the ``project_setup.py`` script for this example:

.. literalinclude:: ../../../examples/cfx_static_mixer/project_setup.py
    :language: python
    :lines: 23-
    :caption: project_setup.py

This example uses this ``exec_cfx.py`` execution script instead of a solver command line:

.. literalinclude:: ../../../examples/cfx_static_mixer/exec_cfx.py
    :language: python
    :lines: 23-
    :caption: exec_cfx.py

Download the ZIP file for the CFX static mixer example and use
a tool such as 7-Zip to extract the files.

.. _bottom of this page:

.. button-link:: ../_downloads/cfx_static_mixer.zip
    :color: black
    :expand:

    Download ZIP file