.. _example_monitor_topics:

Monitor topics and streams
==========================

This example page consolidates the HPS monitor examples into one place. It
starts with topic discovery using :func:`MonitorClient.list_topics`, then shows
the main stream types exposed by the monitor WebSocket bus for running tasks,
task definitions, and backend services.

Use these examples in this order:

1. Discover available tags and values with :func:`MonitorClient.list_topics`.
2. Subscribe to task-level streams such as logs, host resources, or the process tree.
3. Subscribe to scheduler or service-level streams when you need cluster or backend visibility.

All examples below use the scripts in ``examples/monitor``.

.. _example_monitor_list_topics:

List monitor topics
-------------------

This example shows how to use :func:`MonitorClient.list_topics` to discover all
tag keys and their currently active values on the HPS monitor WebSocket bus.
Use this as a first step when building a monitoring integration because it tells
you which tasks, evaluators, log files, and metric streams are currently visible
before you commit to a targeted subscription.

Background
^^^^^^^^^^

The HPS monitor service is a WebSocket-based pub/sub bus. Every message on the
bus carries a set of key-value tags such as ``task_id``, ``file_path``, and
``evaluator_name`` that describe what the message relates to.
:func:`MonitorClient.list_topics` sends a ``list_tags`` command over the
WebSocket and returns a dictionary mapping every known tag key to all values
that currently appear on the bus.

Typical tag keys include:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Tag key
     - Meaning
   * - ``task_id``
     - IDs of tasks that have active evaluator log streams.
   * - ``evaluator_name``
     - Names of evaluators currently connected to the monitor service.
   * - ``client_type``
     - Log source type, for example ``ansys.rep.evaluator.file_tail`` for
       file-tail streams or ``ansys.rep.evaluator.host_resources`` for
       host metrics.
   * - ``file_path``
     - Names of log files currently being tailed, for example
       ``console_output.txt``.
   * - ``job_id``
     - Job IDs associated with active streams.
   * - ``project_id``
     - Project IDs associated with active streams.
   * - ``status``
     - Status tags attached to active streams.

How the example works
^^^^^^^^^^^^^^^^^^^^^

The script follows the standard three-step setup shared by all monitor examples:

1. **Authenticate** with the top-level :class:`Client`. This performs the
   Keycloak OAuth exchange and stores the access token.
2. **Create a** :class:`MonitorClient`. Pass ``client=hps`` so that the
   monitor client can reuse the same HTTP session for monitor calls and for any
   JMS/RMS lookups required by methods such as
   :func:`MonitorClient.stream_task_host_resources`, and pass
   ``ws_connection_options`` to disable TLS certificate verification when
   connecting to a local server with a self-signed certificate.
3. **Call** :func:`MonitorClient.list_topics`. The call is synchronous: it
   opens a short-lived WebSocket connection, sends the ``list_tags`` command,
   waits for the response, and returns the result as a plain Python dictionary.

The ``exclude_noisy`` parameter (``True`` by default) suppresses
high-cardinality keys such as ``timestamp`` that change with every message and
are rarely useful for topic discovery.

Command-line options
^^^^^^^^^^^^^^^^^^^^

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
   * - ``--key TAG_KEY``
     - Print only the values for one specific tag key.
   * - ``--task-id TASK_ID``
     - Filter the output to tag keys that include this task ID as a value.
   * - ``--limit N``
     - Maximum number of values to request per tag key (default: 1000).
   * - ``--json``
     - Print raw JSON instead of the human-readable table.
   * - ``--all``
     - Include high-cardinality keys such as ``timestamp`` that are suppressed
       by default.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
^^^^^^^^^^^^^^^

A typical run while two tasks are running produces output like this::

    TAG KEY                         COUNT  VALUES
    ----------------------------------------------------------------------------------------
    client_type                         3  ansys.rep.evaluator.file_tail
                                           ansys.rep.evaluator.host_resources
                                           ansys.rep.evaluator.process_tree
    evaluator_name                      1  evaluator-0
    file_path                           2  console_output.txt
                                           fluent.trn
    job_id                              2  033Vub9xM...  033VubA2K...
    project_id                          1  033Vub7fh...
    task_id                             2  033VubFI0...  033VubFI3...

Here is the ``list_topics.py`` script for this example:

.. literalinclude:: ../../../examples/monitor/list_topics.py
    :language: python
    :caption: list_topics.py

.. _example_monitor_stream_task_logs:

Stream task logs
----------------

This example shows how to stream evaluator file-tail log output for a running
task using :func:`MonitorClient.stream_task_logs`. Log lines are delivered over
a WebSocket connection as the evaluator writes them, making this the primary way
to watch solver output in real time without polling the server.

Background
^^^^^^^^^^

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
     - The log line text.
   * - ``time`` / ``timestamp``
     - ISO-8601 timestamp of when the line was written.
   * - ``tags``
     - A nested dictionary with ``task_id``, ``file_path``, ``evaluator_name``,
       and ``client_type``.

The ``backlog`` parameter controls how many historical log lines are replayed
from the server's message buffer on connection. Set it to a larger value such
as 500 to catch up on output that was written before the subscription opened, or
to 0 to receive only new lines going forward.

Filtering by file
^^^^^^^^^^^^^^^^^

When a task produces multiple log files such as ``console_output.txt`` and
``fluent.trn``, you can supply ``file_path`` to narrow the stream to a single
file. Omit it to receive lines from all files interleaved, distinguished by the
``tags["file_path"]`` field in each message.

Command-line options
^^^^^^^^^^^^^^^^^^^^

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
     - Optional log filename to filter, for example ``console_output.txt``.
       Omit to receive all files.
   * - ``--backlog``
     - Number of historical log lines to replay on connect (default: 200).
   * - ``--max-messages``
     - Stop after receiving this many messages. Omit for continuous streaming.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
^^^^^^^^^^^^^^^

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

.. _example_monitor_stream_task_host_resources:

Stream task host resources
--------------------------

This example shows how to stream host CPU and memory utilisation metrics for a
running task using :func:`MonitorClient.stream_task_host_resources`. Unlike
:func:`~MonitorClient.stream_task_logs`, this method requires both a project ID
and task ID. It automatically resolves the evaluator assigned to the task through JMS and
RMS and subscribes to that evaluator's ``host_resources`` metric stream.

Background
^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^

:func:`MonitorClient.stream_task_host_resources` looks up the task via the JMS
API, finds the evaluator name from the task's execution context, then queries
the RMS API to resolve the evaluator's host identifier. This is why passing
``client=hps`` when constructing :class:`MonitorClient` is required: the method
uses that pre-authenticated client for JMS/RMS API calls.

Because JMS tasks are scoped by project,
:func:`MonitorClient.stream_task_host_resources` needs both ``task_id`` and
``project_id``.

If you know ``task_id`` but not ``project_id``, use
:func:`MonitorClient.resolve_project_id_for_task` before calling
:func:`MonitorClient.stream_task_host_resources`.

Display modes
^^^^^^^^^^^^^

The example supports two display modes selected by ``--interval``:

* **Per-message mode** (default, ``--interval 0``): prints one line per metric
  snapshot as it arrives, showing the timestamp, CPU usage, and memory percent.
* **Rolling-summary mode** (``--interval N``): accumulates snapshots for *N*
  seconds and then prints a single summary line with the last, minimum,
  maximum, and average values for both CPU and memory over that window.

Command-line options
^^^^^^^^^^^^^^^^^^^^

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
   * - ``--project-id``
     - Optional ID of the project that owns ``--task-id``. If omitted, the
       script infers it from task logs.
   * - ``--backlog``
     - Number of historical metric snapshots to replay on connect (default: 20).
   * - ``--interval SECONDS``
     - If greater than zero, print a rolling summary every *N* seconds instead
       of printing each raw message.
   * - ``--max-messages``
     - Stop after receiving this many snapshots. Omit for continuous streaming.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
^^^^^^^^^^^^^^^

Per-message mode::

    Streaming host resources for project 03P7JeAj5L0vjX7B8u4JQ2, task 033VubFI0m4PYEREddzbN1
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

.. _example_monitor_stream_task_process_tree:

Stream task process tree
------------------------

This example shows how to stream process-tree snapshots for a running task using
:func:`MonitorClient.stream_task_process_tree`. Each snapshot contains every
process in the task's process group, including the task wrapper, the solver,
any co-processes, and their parent-child relationships.

Background
^^^^^^^^^^

The HPS evaluator periodically walks the process group of the task it is running
and publishes a snapshot as a metric message on the monitor bus.
:func:`MonitorClient.stream_task_process_tree` subscribes to the
``client_type=ansys.rep.evaluator.process_tree`` tag for the given task and
yields one dictionary per snapshot.

Message format
^^^^^^^^^^^^^^

The ``message`` field of each yielded dictionary is a JSON string whose payload
is the root process node with nested ``children``::

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

Note that ``cpu_percentage`` and ``memory_percentage`` are strings, not
floats. The example's ``_extract_processes`` helper recursively flattens this
tree into a plain list, and callers must cast these fields with ``float()``
before arithmetic.

Flattening the tree
^^^^^^^^^^^^^^^^^^^

The ``_extract_processes`` function uses a recursive ``_flatten`` helper to
convert the nested JSON tree into a flat list of process dictionaries. Once
flattened, processes can be sorted by CPU usage, filtered by name, or used to
compute aggregate statistics without recursion.

Display modes
^^^^^^^^^^^^^

The example supports three display modes:

* **Flat sorted view** (default): prints each snapshot as a table sorted by CPU
  usage descending, one process per row.
* **Tree view** (``--tree``): indents child processes under their parent using
  the ``ppid`` field to reconstruct the parent-child hierarchy.
* **Rolling-summary mode** (``--interval N``): accumulates snapshots for *N*
  seconds and prints a single summary line showing the snapshot count, process
  count range, and the process with peak CPU usage over the window.

Command-line options
^^^^^^^^^^^^^^^^^^^^

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
     - Stop after receiving this many snapshots. Omit for continuous streaming.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
^^^^^^^^^^^^^^^

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

.. _example_monitor_stream_scheduler_job_status:

Stream scheduler job status
---------------------------

This example shows how to stream job scheduler status metrics for a task
definition using :func:`MonitorClient.stream_scheduler_job_status`. Unlike
task-level methods such as :func:`~MonitorClient.stream_task_logs`, this method
takes a task definition ID rather than a task ID and requires no evaluator
resolution.

Background
^^^^^^^^^^

When HPS submits jobs to an external scheduler such as Slurm or LSF, the
autoscaling service (``ansys.rep.scaling``) periodically publishes a
``scaler_instances`` metric message on the monitor bus. Each message reports
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
^^^^^^^^^^^^^^^^^^^^^

The script follows three steps:

1. **Authenticate**: call :class:`~ansys.hps.client.Client` with your username
   and password to obtain an access token.
2. **Create a** :class:`MonitorClient`: pass ``base_url`` and the token. No
   ``client=`` argument is needed because scheduler job status does not require
   JMS or RMS evaluator resolution.
3. **Stream**: iterate over
   :func:`~MonitorClient.stream_scheduler_job_status`, printing each status
   update as it arrives. Press **Ctrl+C** to stop.

Command-line options
^^^^^^^^^^^^^^^^^^^^

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
     - Stop after receiving this many messages. Omit for continuous streaming.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Expected output
^^^^^^^^^^^^^^^

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

.. _example_monitor_stream_service_logs:

Stream service logs
-------------------

This example shows how to stream log messages from HPS backend services such as
the Job Management Service, autoscaling, or housekeeper using
:func:`MonitorClient.stream_service_logs`. Logs are delivered over a WebSocket
connection in real time, making this useful for debugging service behavior and
monitoring backend operations.

Background
^^^^^^^^^^

HPS runs several backend services that emit operational logs and diagnostics.
These services include:

- **JMS** (Job Management Service): Handles job lifecycle and execution
- **Scaling**: Autoscaling decisions and instance management
- **Housekeeper**: Cleanup and maintenance tasks
- **Evaluator**: Evaluator process metrics and state transitions

:func:`MonitorClient.stream_service_logs` subscribes to messages from a specific
service using the ``client_type`` tag. Use :class:`ClientType` constants for
well-known services, or pass a custom service identifier.

Each yielded message dictionary contains:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Key
     - Content
   * - ``message``
     - The log message text, or a structured object.
   * - ``time`` / ``timestamp``
     - ISO-8601 timestamp of when the message was logged.
   * - ``tags``
     - A nested dictionary with ``client_type`` and other service-specific tags.

The ``backlog`` parameter controls how many historical messages are replayed
from the server's message buffer on connection. Set it to a larger value such
as 500 to catch up on messages that were written before the subscription opened,
or to 0 to receive only new messages going forward.

Available services
^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Service
     - Purpose
   * - ``jms``
     - Job Management Service: job lifecycle and task execution
   * - ``scaling``
     - RMS autoscaling: resource provisioning and instance events
   * - ``housekeeper``
     - Cleanup and maintenance: temporary file removal and resource cleanup
   * - ``evaluator``
     - Evaluator metrics: process state, CPU or memory usage, and events

Command-line options
^^^^^^^^^^^^^^^^^^^^

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
   * - ``--service``
     - Service to stream logs from: ``jms``, ``scaling``, ``housekeeper``, or
       ``evaluator`` (default: ``jms``).
   * - ``--backlog``
     - Number of historical messages to replay on connect (default: 100).
   * - ``--max-messages``
     - Stop after receiving this many messages. Omit for continuous streaming.
   * - ``--list-services``
     - Print available services and exit.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Example usage
^^^^^^^^^^^^^

Stream JMS logs continuously::

    python examples/monitor/stream_service_logs.py \
        --base-url https://localhost:8443/hps \
        --username repadmin \
        --password repadmin \
        --service jms \
        --insecure

Stream scaling service logs with a 500-message backlog and stop after 100 messages::

    python examples/monitor/stream_service_logs.py \
        --base-url https://localhost:8443/hps \
        --username repadmin \
        --password repadmin \
        --service scaling \
        --backlog 500 \
        --max-messages 100 \
        --insecure

Expected output
^^^^^^^^^^^^^^^

A typical run streaming JMS logs produces output like this::

    Streaming logs from service: jms
    Press Ctrl+C to stop
    ----------------------------------------------------------------------------------------
    2026-06-29T14:26:10 Job 033VubFI0m4PYEREddzbN1 submitted successfully
    2026-06-29T14:26:12 Assigned 2 evaluator instances for job 033VubFI0m4PYEREddzbN1
    2026-06-29T14:26:15 Task 033VubFI0m4PYEREddzbN1 started on evaluator node-001
    2026-06-29T14:27:03 Task 033VubFI0m4PYEREddzbN1 completed with exit code 0
    ...

Here is the ``stream_service_logs.py`` script for this example:

.. literalinclude:: ../../../examples/monitor/stream_service_logs.py
    :language: python
    :caption: stream_service_logs.py