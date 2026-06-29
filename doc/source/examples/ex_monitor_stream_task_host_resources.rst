.. _example_monitor_stream_task_host_resources:

Stream task host resources
==========================

This example shows how to stream host CPU and memory utilisation metrics for a
running task using :func:`MonitorClient.stream_task_host_resources`.  Unlike
:func:`~MonitorClient.stream_task_logs`, this method requires only a task ID —
it automatically resolves the evaluator assigned to the task through JMS and
RMS and subscribes to that evaluator's ``host_resources`` metric stream.

Background
----------

The HPS evaluator periodically publishes a snapshot of the host machine's CPU
and memory state as a metric message on the monitor bus.
:func:`MonitorClient.stream_task_host_resources` subscribes to the
``client_type=ansys.rep.evaluator.host_resources`` tag for the evaluator
running the given task and yields one dictionary per snapshot.

The ``message`` field of each yielded dictionary is a JSON string with the
following structure::

    {
        "cpu": {
            "usage": 62.5,
            "per_core": [55.1, 68.2, 70.3, 56.4]
        },
        "virtual_memory": {
            "percent": 96.3,
            "total": 34359738368,
            "available": 1236172800,
            "used": 33123565568
        },
        "swap_memory": { ... },
        "disk_io": { ... }
    }

The example's ``_extract_metrics`` helper parses this payload and returns
``(cpu_usage, memory_percent)`` as floats, handling the case where the field is
absent or unparsable.

Evaluator resolution
--------------------

:func:`MonitorClient.stream_task_host_resources` looks up the task via the JMS
API, finds the evaluator name from the task's execution context, then queries
the RMS API to resolve the evaluator's host identifier.  This is why passing
``client=hps`` when constructing :class:`MonitorClient` is important — it allows
the monitor client to reuse the already-authenticated session for those internal
API calls instead of creating a second login.

Display modes
-------------

The example supports two display modes selected by ``--interval``:

* **Per-message mode** (default, ``--interval 0``): prints one line per metric
  snapshot as it arrives, showing the timestamp, CPU usage, and memory percent.
* **Rolling-summary mode** (``--interval N``): accumulates snapshots for *N*
  seconds and then prints a single summary line with the last, minimum, maximum,
  and average values for both CPU and memory over that window.  This is useful
  for longer runs where per-message output would be too noisy.

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
     - ID of the task to stream host metrics for (required).
   * - ``--backlog``
     - Number of historical metric snapshots to replay on connect (default: 20).
   * - ``--interval SECONDS``
     - If greater than zero, print a rolling summary every *N* seconds instead
       of printing each raw message.
   * - ``--max-messages``
     - Stop after receiving this many snapshots.  Omit for continuous streaming.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
---------------

Per-message mode::

    Streaming host resources for task 033VubFI0m4PYEREddzbN1
    (resolving evaluator via JMS/RMS...)
    Press Ctrl+C to stop
    time                    cpu        mem
    ----------------------------------------------------------------------------------------
    2026-06-26T15:18:44    62.5%     96.3%
    2026-06-26T15:18:49    64.4%     96.4%
    2026-06-26T15:18:57    74.2%     97.0%

Rolling-summary mode (``--interval 30``)::

    time_utc              n    cpu_last  cpu_min  cpu_max  cpu_avg   mem_last  mem_min  mem_max  mem_avg
    ----------------------------------------------------------------------------------------
    2026-06-26T15:19:00      5     74.2    62.5    74.2    67.3      97.0    96.3    97.0    96.7

Here is the ``stream_task_host_resources.py`` script for this example:

.. literalinclude:: ../../../examples/monitor/stream_task_host_resources.py
    :language: python
    :caption: stream_task_host_resources.py
