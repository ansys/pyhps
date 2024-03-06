Managing users
==============

Query user information
----------------------

The :exc:`AuthApi <ansys.hps.client.auth.api.AuthApi>` wraps around a very limited subset
of the `Keycloak Administration REST API <https://www.keycloak.org/documentation>`_,
mostly to allow you to query basic user information.

For example, you can search for a user given their first name:

.. code-block:: python

    from ansys.hps.client import Client
    from ansys.hps.client.auth import AuthApi, User

    cl = Client(
        url="https://127.0.0.1:8443/hps", username="repuser", password="repuser"
    )

    auth_api = AuthApi(cl)
    users = auth_api.get_users(firstName="john", exact=False)

You can also find the email of the user that created and last modified a resource in JMS, for instance a job:

.. code-block:: python
    
    from ansys.hps.client import Client, ProjectApi, AuthApi
    
    cl = Client(
        url="https://127.0.0.1:8443/hps", username="repuser", password="repuser"
    )
    
    project_api = ProjectApi(cl, "02vtv2dI3QdpFSMq4wnDJQ")
    auth_api = AuthApi(cl)
    
    job = project_api.get_jobs()[0]
    
    created_by = auth_api.get_user(id=job.created_by)
    modified_by = auth_api.get_user(id=job.modified_by)
    
    print(
        f"Job '{job.name}' was created by '{created_by.username}' (email: {created_by.email}) "
        f"and last modified by '{modified_by.username}' (email: {created_by.email})"
    )


Using ``python-keycloak`` to modify and create users
----------------------------------------------------

Administrative users with the Keycloak realm management ``manage-users`` role
can create, modify, and delete users.
This functionality is not exposed in the :exc:`AuthApi <ansys.hps.client.auth.api.AuthApi>`.
However, third-party Python packages can be used. 

The following examples show how to modify and create users using the
`python-keycloak <https://pypi.org/project/python-keycloak/>`_ package.

Connect to the Keycloak Admin API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connecting as Keycloak administrator (using default credentials) gives you full control:

.. code-block:: python

    from keycloak import KeycloakAdmin

    keycloak_client = KeycloakAdmin(
        server_url="https://localhost:8443/hps/auth/",
        username="keycloak",
        password="keycloak123",
        realm_name="rep",
        user_realm_name="master",
        verify=False,
    )

Alternatively, you can also connect as a regular user:

.. code-block:: python

    from keycloak import KeycloakAdmin

    keycloak_client = KeycloakAdmin(
        server_url="https://localhost:8443/hps/auth/",
        username="repuser",
        password="repuser",
        realm_name="rep",
        verify=False,
        client_id="rep-cli",
    )

Modify the password of a default user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
    user = keycloak_client.get_users(query={"username": "repuser"})[0]
    
    user["credentials"] = [
        {
            "type": "password",
            "value": "my_new_password",
        }
    ]
    keycloak_client.update_user(user["id"], user)


Create a new user with a temporary password
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    new_user = {
        "username": "test_user", 
        "enabled": True,
                "credentials": [
                    {
                        "value": "temp-password",
                        "type": "password",
                        "temporary": True,
                    }
                ],
        "email": "test-user@test.com", 
        "firstName": "Test",
        "lastName": "User",
        }

    user_id = keycloak_client.create_user(new_user)
    print(f"User ID: {user_id}")
