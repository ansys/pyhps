Monitor Service
===============

Ansys HPS includes a Monitor Service that provides real-time streaming of logs and
metrics from running evaluators and HPS services over WebSocket, as well as build
metadata over REST.

The ``ansys.hps.client.monitor`` Python subpackage provides a client for the monitor
REST and WebSocket interfaces.

APIs
----

.. module:: ansys.hps.client.monitor.api

.. autosummary::
   :toctree: _autosummary

   MonitorApi
   ClientType

Models
------

.. module:: ansys.hps.client.monitor

.. autosummary::
   :toctree: _autosummary

   BuildInfoResponse
   MonitorMessage
   MessageEnvelope
   ListTagsCommand
   ListTagsResponse
   SubscribeCommand