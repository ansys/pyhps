.. _example_mapdl_linked_analyses:

MAPDL linked analyses
=====================

This example shows how to submit an MAPDL linked analysis workflow (prestress-modal-harmonic)
as a multi-task job to REP. The script shows two possible ways to submit the individual tasks:

- All-at-once: All three tasks are defined and included in the job definition before pushing it
  out to the server. When the job is created, it already has three tasks.

  .. code:: bash

      python project_setup.py

- One-by-one: The first task is defined and pushed out to the server. After this first job is created
  and submitted, the second task is added to the job definition and the running job is synced
  to reflect the changes. Finally, the same actions are performed for the third task.

  .. code:: bash

      python project_setup.py --incremental

In both cases, output files from upstream tasks are used as inputs of downstream tasks.

.. only:: builder_html

     You can download the :download:`ZIP file <../../../build/mapdl_linked_analyses.zip>` for the
     MAPDL linked analyses example and use a tool such as 7-Zip to extract the files.

Here is the ``project_setup.py`` file for this project:.

.. literalinclude:: ../../../examples/mapdl_linked_analyses/project_setup.py
    :language: python
    :caption: project_setup.py
