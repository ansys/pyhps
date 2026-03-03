Route Creation Service (RCS)
============================

Ansys HPS includes the Route Creation Service (RCS), which is the main service
for managing route creation and related operations.

The ``ansys.hps.client.rcs`` Python subpackage wraps around the RCS REST API, which
is available at ``https://hostname:port/hps/rcs/api``.

APIs
----

.. module:: ansys.hps.client.rcs.api

.. autosummary::
   :toctree: _autosummary

   RcsApi

Resources
---------

.. module:: ansys.hps.client.rcs

.. autosummary::
   :toctree: _autosummary

   RegisterInstance
   RegisterInstanceResponse
   UnRegisterInstance
   UnRegisterInstanceResponse