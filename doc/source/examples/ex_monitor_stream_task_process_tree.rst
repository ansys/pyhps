.. _example_monitor_stream_task_process_tree:

Stream task process tree
========================

This example shows how to stream process-tree snapshots for a running task using
:func:`MonitorClient.stream_task_process_tree`.  Each snapshot contains every
process in the task's process group — the task wrapper, the solver, any
co-processes (for example a Cortex post-processor or licence manager), and their
parent-child relationships.  This gives a fine-grained view of which processes
are active and how CPU and memory are distributed across them during a solve.

Background
----------

The HPS evaluator periodically walks the process group of the task it is running
and publishes a snapshot as a metric message on the monitor bus.
:func:`MonitorClient.stream_task_process_tree` subscribes to the
``client_type=ansys.rep.evaluator.process_tree`` tag for the given task and
yields one dictionary per snapshot.

Message format
--------------

The ``message`` field of each yielded dictionary is a JSON string whose payload
is the *root* process node with nested ``children``::

    {
        "pid": 18508,
        "ppid": 0,
        "name": "task_033VubFI0m4PYEREddzbN1",
        "cpu_percentage": "0.2",
        "memory_percentage": "0.5",
        "state": "running",
        "level": 0,
        "children": [
            {
                "pid": 17904,
                "ppid": 18508,
                "name": "cmd.exe",
                "cpu_percentage": "0.0",
                "memory_percentage": "0.0",
                "state": "running",
                "level": 1,
                "children": [
                    {
                        "pid": 14636,
                        "ppid": 17904,
                        "name": "cx2610.exe",
                        "cpu_percentage": "14.1",
                        "memory_percentage": "2.3",
                        "state": "running",
                        "level": 2,
                        "children": [ ... ]
                    }
                ]
            }
        ]
    }

Note that ``cpu_percentage`` and ``memory_percentage`` are *strings*, not
floats.  The example's ``_extract_processes`` helper recursively flattens this
tree into a plain list (stripping the ``children`` key from each node) and
callers must cast these fields with ``float()`` before arithmetic.

Flattening the tree
-------------------

The ``_extract_processes`` function uses a recursive ``_flatten`` helper to
convert the nested JSON tree into a flat list of process dictionaries.  This is
necessary because the server encodes the entire tree as a single root node, not
as a list.  Once flattened, processes can be sorted by CPU usage, filtered by
name, or used to compute aggregate statistics without recursion.

Display modes
-------------

The example supports three display modes:

* **Flat sorted view** (default): prints each snapshot as a table sorted by CPU
  usage descending, one process per row.
* **Tree view** (``--tree``): indents child processes under their parent using
  the ``ppid`` field to reconstruct the parent-child hierarchy, matching the
  structure reported by the OS process tree.
* **Rolling-summary mode** (``--interval N``): accumulates snapshots for *N*
  seconds and prints a single summary line showing the snapshot count, process
  count range, and the process with peak CPU usage over the window.

Command-line options
--------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Option
     - Description
   * - ``--base-url``
     - Base URL of the HPS server (default: ``https://localhost:8443/hps``).
   * - ``--username``
     - HPS username.
   * - ``--password``
     - HPS password.
   * - ``--task-id``
     - ID of the task to stream process-tree snapshots for (required).
   * - ``--backlog``
     - Number of historical snapshots to replay on connect (default: 20).
   * - ``--tree``
     - Show child processes indented under their parent instead of a flat
       sorted list.
   * - ``--interval SECONDS``
     - If greater than zero, print a rolling summary every *N* seconds instead
       of printing each snapshot in full.
   * - ``--max-messages``
     - Stop after receiving this many snapshots.  Omit for continuous streaming.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
---------------

Flat sorted view during an active Fluent solve::

    Streaming process-tree snapshots for task 033VubFI0m4PYEREddzbN1
    Press Ctrl+C to stop
    ----------------------------------------------------------------------------------------
    2026-06-26T15:19:00  [9 processes]
      pid      name                       cpu        mem  status
      ----------------------------------------------------------------
      14636    cx2610.exe              14.1%      2.3%  running
      24088    fl2610.exe               9.7%      2.1%  running
      23648    ansyscl.exe              0.3%      0.1%  running
      18508    task_033VubFI0m4...      0.0%      0.5%  running
      ...

Tree view (``--tree``) of the same snapshot::

    2026-06-26T15:19:00  [9 processes]
      pid      name                       cpu        mem  status
      ----------------------------------------------------------------
      18508    task_033VubFI0m4...      0.0%      0.5%  running
        17904    cmd.exe                0.0%      0.0%  running
          45592    fluent.exe           0.0%      0.0%  running
          14636    cx2610.exe          14.1%      2.3%  running
          24088    fl2610.exe           9.7%      2.1%  running
          23648    ansyscl.exe          0.3%      0.1%  running

Here is the ``stream_task_process_tree.py`` script for this example:

.. literalinclude:: ../../../examples/monitor/stream_task_process_tree.py
    :language: python
    :caption: stream_task_process_tree.py
