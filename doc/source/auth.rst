Authentication Service
===========================

The DCS Authentication Service processes all DCS sign ins following OAuth 2.0 resource owner password credentials flow. 
When you enter your DCS credentials, you get an access token (expiring after 24 hours) and a refresh token for authenticating all services.

The Authentication Python client wraps around the Authentication Service REST API available at ``https://hostname/dcs/auth/api``.

Authentication function
------------------------------------------
.. autofunction:: ansys.rep.client.auth.authenticate


Client object
------------------------------------------
.. autoclass:: ansys.rep.client.auth.Client
   :members:


User
--------------------------------------
.. autoclass:: ansys.rep.client.auth.User
   :members: