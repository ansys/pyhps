Exception handling
------------------

All exceptions that the Ansys REP client explicitly raises inherit from the :exc:`ansys.hps.client.HPSError`
base class. Client errors are raised for 4xx HTTP status codes, while API errors are raised for 5xx HTTP
status codes (server-side errors).

For example, instantiating a client with invalid credentials returns a 401 client error:

.. code-block:: python

    from ansys.hps.client import Client, HPSError

    try:
        client = Client(url="https://localhost:8443/rep/", username="repuser",  password="wrong_psw")
    except HPSError as e:
        print(e)

    #Output:
    # 401 Client Error: invalid_grant for: POST https://localhost:8443/rep/auth/realms/rep/protocol/openid-connect/token
    # Invalid user credentials

A *get* call on a non-existing resource returns a 404 client error:

.. code-block:: python

    from ansys.hps.client.jms import JmsApi

    jms_api = JmsApi(client)
    try:
        jms_api.get_project(id="non_existing_project")
    except HPSError as e:
        print(e)

    #Output:
    #404 Client Error: Not Found for: GET https://localhost:8443/rep//jms/api/v1/projects/non_existing_project
