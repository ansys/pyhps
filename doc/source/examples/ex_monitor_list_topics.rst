.. _example_monitor_list_topics:

List monitor topics
===================

This example shows how to use :func:`MonitorClient.list_topics` to discover all
tag keys and their currently active values on the HPS monitor WebSocket bus.
Use this as a first step when building a monitoring integration — it tells you
exactly which tasks, evaluators, log files, and metric streams are visible before
you commit to a targeted subscription.

Background
----------

The HPS monitor service is a WebSocket-based pub/sub bus.  Every message on the
bus carries a set of key-value *tags* (for example ``task_id``, ``file_path``,
``evaluator_name``) that describe what the message relates to.
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
     - Names of log files currently being tailed (for example
       ``console_output.txt``).
   * - ``job_id``
     - Job IDs associated with active streams.
   * - ``project_id``
     - Project IDs associated with active streams.
   * - ``status``
     - Status tags attached to active streams.

How the example works
---------------------

The script follows the standard three-step setup shared by all monitor examples:

1. **Authenticate** with the top-level :class:`Client`.  This performs the
   Keycloak OAuth exchange and stores the access token.
2. **Create a** :class:`MonitorClient`.  Pass ``client=hps`` so that the
   monitor client can reuse the same HTTP session for any JMS/RMS look-ups it
   needs internally, and pass ``ws_connection_options`` to disable TLS
   certificate verification when connecting to a local server with a self-signed
   certificate.
3. **Call** :func:`MonitorClient.list_topics`.  The call is synchronous — it
   opens a short-lived WebSocket connection, sends the ``list_tags`` command,
   waits for the response, and returns the result as a plain Python dictionary.

The ``exclude_noisy`` parameter (``True`` by default) suppresses
high-cardinality keys such as ``timestamp`` that change with every message and
are rarely useful for topic discovery.

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
---------------

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
