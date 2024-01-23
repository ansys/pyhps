Exceptions
===========================

HTTP requests returning an unsuccessful status code raise:

* :exc:`ansys.hps.core.ClientError` for client errors (4xx status code. For example, bad syntax or not found)
* :exc:`ansys.hps.core.APIError` for server errors (5xx status code. For example, internal server error or not implemented)

All exceptions that the Ansys REP clients explicitly raise inherit from :exc:`ansys.hps.core.HPSError`.

.. autoexception:: ansys.hps.core.HPSError
   :members:
   
.. autoexception:: ansys.hps.core.APIError
.. autoexception:: ansys.hps.core.ClientError