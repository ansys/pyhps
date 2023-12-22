Authentication Service
===========================

--TODO Review-- 

The REP Authentication Service processes all REP sign ins following OAuth 2.0 resource owner password credentials flow. 
When you enter your REP credentials, you get an access token (expiring after 24 hours) and a refresh token for authenticating all services.

The ``ansys.hps.client.auth`` subpackage wraps around the Authentication Service REST API available at ``https://hostname:port/rep/auth/api``.

Authentication function
------------------------------------------
.. autofunction:: ansys.hps.client.auth.authenticate


Auth API
------------------------------------------
.. autoclass:: ansys.hps.client.auth.AuthApi
   :members:


User
--------------------------------------
.. autoclass:: ansys.hps.client.auth.User
   :members: