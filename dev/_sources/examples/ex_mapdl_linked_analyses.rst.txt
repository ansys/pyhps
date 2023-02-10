.. _example_mapdl_linked_analyses:

MAPDL Linked Analyses Example
=========================================

This example shows how to submit an MAPDL linked analysis workflow (prestress-modal-harmonic)
as a multi-task job to REP. The script shows two possible ways to submit the individual tasks:

1. All-at-one: all 3 tasks are defined and included in the job definition before pushing it out to the server. When the job is created, it already has 3 tasks.

    .. code:: bash

        python project_setup.py

2. One-by-one: the first task is defined, pushed out to the server and then the job is created and submitted. Then, the second task is added to the job definition and the running job is synced to reflect the changes. The same for the third task.

    .. code:: bash

        python project_setup.py --incremental

In both cases, output files from upstream tasks are used as input of downstream ones.

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`MAPDL Linked Analyses Example <../../../build/mapdl_linked_analyses.zip>`.


.. literalinclude:: ../../../examples/mapdl_linked_analyses/project_setup.py
    :language: python
    :caption: project_setup.py