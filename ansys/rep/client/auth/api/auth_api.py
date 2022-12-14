# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri, O.Koenig
# ----------------------------------------------------------

from typing import List

from keycloak import KeycloakAdmin

from ansys.rep.client.exceptions import REPError

from ..resource import User
from ..schema.user import UserSchema


class AuthApi:
    """A python interface to the Authorization Service API.

    Users with admin rights (such as the default ``repadmin`` user) can create new
    users as well as modify or delete existing ones. Non-admin users are only allowed
    to query the list of existing users.

    Args:
        rep_url (str): The base path for the server to call, e.g. "https://127.0.0.1:8443/rep".
        username (str): Username
        password (str): Password

    Example:

        >>> from ansys.rep.client.auth import Client, User
        >>> cl = Client(
                rep_url="https://127.0.0.1:8443/rep/", username="repadmin", password="repadmin"
            )
        >>> existing_users = cl.get_users()
        >>> new_user = User(username='test_user', password='dummy',
        >>>                 email='test_user@test.com', fullname='Test User',
        >>>                 is_admin=False)
        >>> cl.create_user(new_user)

    """

    def __init__(self, client):
        self.client = client

    @property
    def url(self):
        return f"{self.client.rep_url}/auth/"

    def get_users(self, as_objects=True) -> List[User]:
        """Return a list of users."""
        return get_users(self.client, as_objects=as_objects)

    def create_user(self, user: User, as_objects=True) -> User:
        """Create a new user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
            as_objects (bool, optional): Defaults to True.
        """
        return create_user(self.client, user, as_objects=as_objects)

    def update_user(self, user: User, as_objects=True) -> User:
        """Modify an existing user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
            as_objects (bool, optional): Defaults to True.
        """
        return update_user(self.client, user, as_objects=as_objects)

    def delete_user(self, user: User) -> None:
        """Delete an existing user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
        """
        return delete_user(self.client, user)


def _admin_client(client):

    if client.access_token is None:
        raise REPError(
            "Missing access token. You need to authenticate with "
            "the username and password workflow to be able to operate "
            "Keycloak as admin."
        )

    custom_headers = {
        "Authorization": "Bearer " + client.access_token,
        "Content-Type": "application/json",
    }
    keycloak_admin = KeycloakAdmin(
        server_url=client.auth_api_url,
        username=None,
        password=None,
        realm_name=client.realm,
        client_id=client.client_id,
        verify=False,
        custom_headers=custom_headers,
    )
    return keycloak_admin


def get_users(client, as_objects=True):
    admin = _admin_client(client)
    data = admin.get_users({})
    for d in data:
        uid = d["id"]
        groups = admin.get_user_groups(uid)
        d["groups"] = [g["name"] for g in groups]
        realm_roles = admin.get_realm_roles_of_user(uid)
        d["realm_roles"] = [r["name"] for r in realm_roles]
        d["is_admin"] = d  # Force admin check

    schema = UserSchema(many=True)
    users = schema.load(data)
    return users


def create_user(client, user, as_objects=True):
    schema = UserSchema(many=False)
    data = schema.dump(user)

    pwd = data.pop("password", None)
    if pwd is not None:
        data["credentials"] = [
            {
                "type": "password",
                "value": pwd,
            }
        ]
    data["enabled"] = True

    admin = _admin_client(client)
    uid = admin.create_user(data)
    data = admin.get_user(uid)
    user = schema.load(data)
    return user


def update_user(client, user, as_objects=True):
    schema = UserSchema(many=False)
    data = schema.dump(user)

    pwd = data.pop("password", None)
    if pwd is not None:
        data["credentials"] = [
            {
                "type": "password",
                "value": pwd,
            }
        ]

    admin = _admin_client(client)
    data = admin.update_user(user.id, data)
    user = schema.load(data)
    return user


def delete_user(client, user):
    admin = _admin_client(client)
    admin.delete_user(user.id)
