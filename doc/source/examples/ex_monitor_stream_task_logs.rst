.. _example_monitor_stream_task_logs:

Stream task logs
================

This example shows how to stream evaluator file-tail log output for a running
task using :func:`MonitorClient.stream_task_logs`.  Log lines are delivered over
a WebSocket connection as the evaluator writes them, making this the primary way
to watch solver output (iteration residuals, convergence history, warnings) in
real time without polling the server.

Background
----------

While a task is running, the HPS evaluator tails one or more log files and
publishes each new line as a tagged message on the monitor WebSocket bus.
:func:`MonitorClient.stream_task_logs` subscribes to the ``task_id`` and
``client_type=ansys.rep.evaluator.file_tail`` tags for the requested task and
yields one dictionary per line.

Each yielded message dictionary contains:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Key
     - Content
   * - ``message``
     - The log line text (a string).
   * - ``time`` / ``timestamp``
     - ISO-8601 timestamp of when the line was written.
   * - ``tags``
     - A nested dictionary with ``task_id``, ``file_path``, ``evaluator_name``,
       and ``client_type``.

The ``backlog`` parameter controls how many historical log lines are replayed
from the server's message buffer on connection.  Set it to a larger value (for
example 500) to catch up on output that was written before the subscription
opened, or to 0 to receive only new lines going forward.

Filtering by file
-----------------

When a task produces multiple log files (for example ``console_output.txt`` and
``fluent.trn``), you can supply ``file_path`` to narrow the stream to a single
file.  Omit it to receive lines from all files interleaved, distinguished by the
``tags["file_path"]`` field in each message.

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
     - ID of the task to stream logs for (required).
   * - ``--file-path``
     - Optional log file name to filter, for example ``console_output.txt``.
       Omit to receive all files.
   * - ``--backlog``
     - Number of historical log lines to replay on connect (default: 200).
   * - ``--max-messages``
     - Stop after receiving this many messages.  Omit for continuous streaming.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
---------------

A typical run streaming a Fluent solver console produces output like this::

    Streaming logs for task 033VubFI0m4PYEREddzbN1
    Press Ctrl+C to stop
    ----------------------------------------------------------------------------------------
    2026-06-26T15:17:43 [console_output.txt]
    2026-06-26T15:17:43 [console_output.txt]         1   1.0000e+00   0.0000e+00   0.0000e+00   0.0000e+00   1.0000e+00  308.0000   0.0000e+00   0.0000e+00   0:00:12      199
    2026-06-26T15:17:44 [console_output.txt]         2   9.8765e-01   1.2340e-03   1.2340e-03   9.8760e-04   9.8765e-01  307.9200   3.4160e-03   0.0000e+00   0:00:11      198
    ...
    2026-06-26T15:19:33 [console_output.txt]        76   9.6758e-03   4.5210e-04   2.3410e-04   1.1230e-04   9.6758e-03  303.3800   4.2100e-05   0.0000e+00   0:00:00        0

Here is the ``stream_task_logs.py`` script for this example:

.. literalinclude:: ../../../examples/monitor/stream_task_logs.py
    :language: python
    :caption: stream_task_logs.py
