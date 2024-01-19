Authentication Service
===========================

--TODO Review-- 

The REP Authentication Service processes all REP sign-ins following the credentials flow
for owner passwords of OAuth 2.0 resources. When you enter your REP credentials, you get an
access token, which expires after 24 hours, and a refresh token for authenticating all services.

The ``ansys.hps.client.auth`` subpackage wraps around the
`REP Authentication Service REST API <https://hostname:port/rep/auth/api>`_.

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