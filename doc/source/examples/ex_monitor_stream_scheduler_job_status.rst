.. _example_monitor_stream_scheduler_job_status:

Stream scheduler job status
============================

This example shows how to stream job scheduler status metrics for a task
definition using :func:`MonitorClient.stream_scheduler_job_status`.  Unlike
task-level methods such as :func:`~MonitorClient.stream_task_logs`, this method
takes a **task definition ID** rather than a task ID and requires no evaluator
resolution — it subscribes directly to the autoscaling service's metric stream.

Background
----------

When HPS submits jobs to an external scheduler such as Slurm or LSF, the
autoscaling service (``ansys.rep.scaling``) periodically publishes a
``scaler_instances`` metric message on the monitor bus.  Each message reports
how many scheduler jobs are currently running, pending, and queued for a given
task definition.

:func:`MonitorClient.stream_scheduler_job_status` subscribes to messages with
the following tags:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Tag
     - Value
   * - ``client_type``
     - ``ansys.rep.scaling``
   * - ``type``
     - ``metric``
   * - ``task_definition_id``
     - The task definition ID you provide.
   * - ``metric_type``
     - ``scaler_instances``

The ``message`` field of each yielded dictionary is a JSON string with the
following structure::

    {
        "running": 2,
        "pending": 1,
        "total": 3,
        "scheduler": "slurm"
    }

The example's ``_extract_counts`` helper parses this payload and returns the
individual counts, handling the case where a field is absent or unparsable.

How the example works
---------------------

The script follows three steps:

1. **Authenticate** — call :class:`~ansys.hps.client.Client` with your
   username and password to obtain an access token.
2. **Create a** :class:`MonitorClient` — pass ``base_url`` and the token.
   No ``client=`` argument is needed because scheduler job status does not
   require JMS/RMS evaluator resolution.
3. **Stream** — iterate over
   :func:`~MonitorClient.stream_scheduler_job_status`, printing each status
   update as it arrives.  Press **Ctrl+C** to stop.

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
   * - ``--task-definition-id``
     - ID of the task definition to stream scheduler status for (required).
   * - ``--backlog``
     - Number of historical metric messages to replay on connect (default: 20).
   * - ``--max-messages``
     - Stop after receiving this many messages.  Omit for continuous streaming.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
---------------

::

    Streaming scheduler job status for task definition taskdef-abc123
    Press Ctrl+C to stop
    time                   scheduler            running      pending     total
    --------------------------------------------------------------------------------
    2026-06-29T10:04:11   slurm              running    2   pending    1   total    3
    2026-06-29T10:04:26   slurm              running    3   pending    0   total    3
    2026-06-29T10:04:41   slurm              running    3   pending    0   total    3

Here is the ``stream_scheduler_job_status.py`` script for this example:

.. literalinclude:: ../../../examples/monitor/stream_scheduler_job_status.py
    :language: python
    :caption: stream_scheduler_job_status.py
