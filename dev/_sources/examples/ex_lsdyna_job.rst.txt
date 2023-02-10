.. _example_lsdyna_job:

LS-DYNA Job Submission
======================

This example shows how to submit an LS-DYNA job to REP. Once submitted, minimal job information are serialized to a JSON file ``rep_job.json``.
This mimics what an application would need to store in order to subsequently monitor the job and download results.

The job consists of two tasks:

* The first task runs the actual LS-DYNA simulation
* The second task runs a little LS-PrePost script to post-process the results of the first task.

Usage:

.. code:: bash
    
    python lsdyna_job.py submit
    python lsdyna_job.py monitor
    python lsdyna_job.py download

.. note::
    The ``download`` action requires ``tqdm`` and ``humanize`` packages to show a progress bar during the result files download. You can install them with ``python -m pip install tqdm humanize``.

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`LS-DYNA Job Submission Example <../../../build/lsdyna_cylinder_plate.zip>`.

.. literalinclude:: ../../../examples/lsdyna_cylinder_plate/lsdyna_job.py
    :language: python
    :caption: lsdyna_job.py