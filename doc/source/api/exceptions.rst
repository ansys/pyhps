Exceptions
==========

HTTP requests returning an unsuccessful status code raise one of these exceptions:

* :exc:`ansys.hps.client.ClientError` for client errors (4xx status code), such as include bad syntax or not found.
* :exc:`ansys.hps.client.APIError` for server errors (5xx status code), such as internal server errors or not implemented.

All exceptions that the Ansys REP clients explicitly raise inherit from :exc:`ansys.hps.client.HPSError`.

.. autoexception:: ansys.hps.client.HPSError
   :members:
   
.. autoexception:: ansys.hps.client.APIError
.. autoexception:: ansys.hps.client.ClientError