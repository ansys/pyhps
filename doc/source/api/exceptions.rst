Exceptions
===========================

HTTP requests returning an unsuccessful status code will raise:

* :exc:`ansys.hps.client.ClientError` for client errors (4xx status code. For example, bad syntax or not found)
* :exc:`ansys.hps.client.APIError` for server errors (5xx status code. For example, internal server error or not implemented)

All exceptions that the Ansys REP clients explicitly raise inherit from :exc:`ansys.hps.client.HPSError`.

.. autoexception:: ansys.hps.client.HPSError
   :members:
   
.. autoexception:: ansys.hps.client.APIError
.. autoexception:: ansys.hps.client.ClientError