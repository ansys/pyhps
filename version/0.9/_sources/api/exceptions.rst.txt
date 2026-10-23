Exceptions
==========

HTTP requests returning an unsuccessful status code raise one of these exceptions:

* :exc:`ansys.hps.client.ClientError` for client errors (4xx status code), such as for included
  bad syntax or not found.
* :exc:`ansys.hps.client.APIError` for server errors (5xx status code), such as for internal server
  errors or not implemented.

All exceptions that a PyHPS client explicitly raises are inherited from the :exc:`ansys.hps.client.HPSError`
base class.

.. module:: ansys.hps.client.exceptions

.. autosummary::
   :toctree: _autosummary

   HPSError
   APIError
   ClientError