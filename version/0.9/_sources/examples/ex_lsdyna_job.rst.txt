.. _example_lsdyna_job:

LS-DYNA job submission
======================

This example shows how to submit an LS-DYNA job to HPS. Once submitted, minimal job
information is serialized to a ``rep_job.json`` file. This mimics what an app would need
to store to subsequently monitor the job and download results.

The job consists of two tasks:

* The first task runs the actual LS-DYNA simulation.
* The second task runs a small LS-PrePost script to postprocess the results of the first task.

**Usage**

.. code:: bash
    
    python lsdyna_job.py submit
    python lsdyna_job.py monitor
    python lsdyna_job.py download

**Notes**

- This example only runs on the Windows platform as the LS-PrePost task must open the LS-PREPOST GUI.
- The ``download`` action requires the ``tqdm`` and ``humanize`` packages to show a progress bar during
  the download of the result files. You can install these packages with this command::

    python -m pip install tqdm humanize

.. only:: builder_html

     You can dowlonad the :download:`ZIP file <../../../build/lsdyna_cylinder_plate.zip>` for
     the LS-DYNA job submission example and use a tool such as 7-Zip to extract the files.

Here is the ``project_setup.py`` script for this example:

.. literalinclude:: ../../../examples/lsdyna_cylinder_plate/lsdyna_job.py
    :language: python
    :lines: 23-
    :caption: lsdyna_job.py
