.. _example_rcs_route_creation:

Route creation service: register and unregister an instance
===========================================================

This example shows how to use the Route Creation Service (RCS) API to register
an external service instance with the HPS reverse proxy and then unregister it
when the session ends.  Registering an instance makes the external service
accessible through the HPS gateway under a path prefix, removing the need for
clients to reach it directly.

Background
----------

HPS includes a Route Creation Service that manages the reverse-proxy routing
table at runtime.  When a solver or external tool registers itself, HPS adds a
route so that HTTP traffic sent to a well-known path on the HPS gateway is
forwarded to that instance's URL.  Unregistering removes the route.

The RCS API is exposed through :class:`ansys.hps.client.rcs.RcsApi` and uses
the same :class:`~ansys.hps.client.Client` authentication as the rest of the
pyhps library.

The registration workflow involves three objects:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Class
     - Purpose
   * - :class:`~ansys.hps.client.rcs.RcsApi`
     - Client for the RCS REST API.  Constructed from an authenticated
       :class:`~ansys.hps.client.Client`.
   * - :class:`~ansys.hps.client.rcs.RegisterInstance`
     - Request body for registering a new instance.  Supply the instance URL,
       a service name, and the routing strategy (``"path_prefix"`` is the
       standard choice).
   * - :class:`~ansys.hps.client.rcs.UnRegisterInstance`
     - Request body for removing a previously registered instance.  Requires
       the ``resource_name`` returned by the register call.

How the example works
---------------------

1. **Connect** to the HPS server using :class:`~ansys.hps.client.Client` with
   the server URL, username, and password.
2. **Create** an :class:`~ansys.hps.client.rcs.RcsApi` from the authenticated
   client.
3. **Health-check** the RCS API with :func:`RcsApi.health_check` to confirm the
   service is reachable before attempting registration.
4. **Register** the instance by calling :func:`RcsApi.register_instance` with a
   :class:`~ansys.hps.client.rcs.RegisterInstance` payload that specifies:

   - ``url`` — the base URL of the instance to expose (for example
     ``https://localhost:8000``).
   - ``service_name`` — an identifier for the type of service (for example
     ``"solver"``).
   - ``routing`` — the routing strategy; ``"path_prefix"`` routes all requests
     whose path begins with the allocated prefix to this instance.

5. **Unregister** the instance by calling :func:`RcsApi.unregister_instance`
   with the ``resource_name`` from the registration response.  This removes the
   route from the gateway immediately.

Command-line options
--------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Option
     - Description
   * - ``-U`` / ``--url``
     - Base URL of the HPS server (default: ``https://localhost:8443/hps``).
   * - ``-i`` / ``--instance_url``
     - URL of the external instance to register (default:
       ``https://localhost:8000``).
   * - ``-u`` / ``--username``
     - HPS username (default: ``repuser``).
   * - ``-p`` / ``--password``
     - HPS password (default: ``repuser``).

Expected output
---------------

A successful run produces output like this::

    Connect to HPC Platform Services
    HPS URL: https://localhost:8443/hps
    RCS API health check: {'status': 'ok'}
    RCS API info: {'version': '1.0.0', ...}
    Register instance with URL: https://localhost:8000
    Register instance response: resource_name='solver-a1b2c3' url='https://localhost:8000' ...
    Unregister instance
    Unregister instance response: resource_name='solver-a1b2c3' status='removed'

Here is the ``rcs_example.py`` script for this example:

.. literalinclude:: ../../../examples/route_creation/rcs_example.py
    :language: python
    :lines: 23-
    :caption: rcs_example.py
