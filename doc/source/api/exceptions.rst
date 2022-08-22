Exceptions
===========================

HTTP requests returning an unsuccessful status code will raise:

* :exc:`ansys.rep.client.ClientError` for client errors (4xx status code, e.g. bad syntax or not found)
* :exc:`ansys.rep.client.APIError` for server errors (5xx status code, e.g. internal server error or not implemented)

All exceptions that the Ansys REP clients explicitly raise inherit from :exc:`ansys.rep.client.REPError`.

.. autoexception:: ansys.rep.client.REPError
   :members:
   
.. autoexception:: ansys.rep.client.APIError
.. autoexception:: ansys.rep.client.ClientError