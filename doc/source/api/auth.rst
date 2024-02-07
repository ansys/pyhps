Authentication service
======================

`Keycloak <https://www.keycloak.org>`_ is used for identity and access management. This open source
solution provides a variety of options for authentication and authorization. Users authenticate
with Keycloak rather than with the application, allowing flexibility in how the sign-in experience
is delivered.

Keycloak is exposed at ``https://hostname:port/hps/auth/api``, which is what the ``ansys.hps.client.auth``
module wraps around.

Authentication function
-----------------------
.. autofunction:: ansys.hps.client.auth.authenticate


Auth API
--------
.. autoclass:: ansys.hps.client.auth.AuthApi
   :members:


User
----
.. autoclass:: ansys.hps.client.auth.User
   :members: