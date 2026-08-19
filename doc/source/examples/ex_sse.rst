.. _example_sse:

Stream operation updates via Server-Sent Events (SSE)
=======================================================

This example demonstrates how to use Server-Sent Events (SSE).
Server-Sent Events offer a more efficient way to monitor long-running operations than polling.

The example shows how to:

1. Authenticate with the HPS server using the standard ``Client`` and ``client_from_args()`` utilities
2. Start a long-running example operation on the server
3. Subscribe to ``operation:updated`` and ``operation:completed`` events via SSE
4. Automatically exit when the operation completes

Here is the ``sse.py`` script:

.. literalinclude:: ../../../examples/sse/sse.py
    :language: python
    :caption: sse.py

Typical usage:

.. code-block:: bash

    python examples/sse/sse.py -u repadmin -p repadmin --sleep 20

The ``--sleep`` argument controls how long the operation should run (in seconds).
The script will stream events in real-time and exit once the operation completes.
