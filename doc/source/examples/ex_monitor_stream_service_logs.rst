.. _example_monitor_stream_service_logs:

Stream service logs
===================

This example shows how to stream log messages from HPS backend services (such as
the Job Management Service, autoscaling, or housekeeper) using
:func:`MonitorClient.stream_service_logs`.  Logs are delivered over a WebSocket
connection in real time, making this useful for debugging service behavior and
monitoring backend operations.

Background
----------

HPS runs several backend services that emit operational logs and diagnostics.
These services include:

- **JMS** (Job Management Service): Handles job lifecycle and execution
- **Scaling**: Autoscaling decisions and instance management
- **Housekeeper**: Cleanup and maintenance tasks
- **Evaluator**: Evaluator process metrics and state transitions

:func:`MonitorClient.stream_service_logs` subscribes to messages from a specific
service using the ``client_type`` tag.  Use :class:`ClientType` constants for
well-known services, or pass a custom service identifier.

Each yielded message dictionary contains:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Key
     - Content
   * - ``message``
     - The log message text (a string or structured object).
   * - ``time`` / ``timestamp``
     - ISO-8601 timestamp of when the message was logged.
   * - ``tags``
     - A nested dictionary with ``client_type`` and other service-specific tags.

The ``backlog`` parameter controls how many historical messages are replayed
from the server's message buffer on connection.  Set it to a larger value (for
example 500) to catch up on messages that were written before the subscription
opened, or to 0 to receive only new messages going forward.

Available services
------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Service
     - Purpose
   * - ``jms``
     - Job Management Service: job lifecycle, task execution
   * - ``scaling``
     - RMS autoscaling: resource provisioning and instance events
   * - ``housekeeper``
     - Cleanup and maintenance: temporary file removal, resource cleanup
   * - ``evaluator``
     - Evaluator metrics: process state, CPU/memory usage, events

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
   * - ``--service``
     - Service to stream logs from: ``jms``, ``scaling``, ``housekeeper``, or
       ``evaluator`` (default: ``jms``).
   * - ``--backlog``
     - Number of historical messages to replay on connect (default: 100).
   * - ``--max-messages``
     - Stop after receiving this many messages.  Omit for continuous streaming.
   * - ``--list-services``
     - Print available services and exit.
   * - ``--insecure``
     - Disable TLS certificate verification (required for local servers with
       self-signed certificates).

Example usage
-------------

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
---------------

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
