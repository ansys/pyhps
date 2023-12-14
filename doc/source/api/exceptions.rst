Exceptions
===========================

HTTP requests returning an unsuccessful status code will raise:

* :exc:`ansys.hps.client.ClientError` for client errors (4xx status code, e.g. bad syntax or not found)
* :exc:`ansys.hps.client.APIError` for server errors (5xx status code, e.g. internal server error or not implemented)

All exceptions that the Ansys REP clients explicitly raise inherit from :exc:`ansys.hps.client.REPError`.

.. autoexception:: ansys.hps.client.REPError
   :members:
   
.. autoexception:: ansys.hps.client.APIError
.. autoexception:: ansys.hps.client.ClientError