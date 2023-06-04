# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri, O.Koenig
# ----------------------------------------------------------

from typing import List

from keycloak import KeycloakAdmin

from ..resource import User
from ..schema.user import UserSchema


class AuthApi:
    """A python interface to the Authorization Service API.

    Users with admin rights (such as the default ``repadmin`` user) can create new
    users as well as modify or delete existing ones. Non-admin users are only allowed
    to query the list of existing users.

    Parameters
    ----------
    client : Client
        A REP client object.

    Examples
    --------

    Get users whose first name contains "john":

    >>> from ansys.rep.client import Client
    >>> from ansys.rep.client.auth import AuthApi, User
    >>> cl = Client(
    ...     rep_url="https://127.0.0.1:8443/rep/", username="repadmin", password="repadmin"
    ... )
    >>> auth_api = AuthApi(cl)
    >>> users = auth_api.get_users(firstName="john", exact=False)

    Create a new user:

    >>> new_user = User(
    ...     username="new_user",
    ...     password="dummy",
    ...     email=f"new_user@test.com",
    ...     first_name="New",
    ...     last_name="User",
    ... )
    >>> auth_api.create_user(new_user)

    """

    def __init__(self, client):
        self.client = client

    @property
    def url(self):
        return f"{self.client.rep_url}/auth/"

    @property
    def keycloak_admin_client(self) -> KeycloakAdmin:
        """Returns an authenticated client for the Keycloak Admin API"""
        return _admin_client(self.client)

    def get_users(self, as_objects=True, **query_params) -> List[User]:
        """Return users, filtered according to query parameters

        Examples of query parameters are:
        - `username`
        - `firstName`
        - `lastName`
        - `exact`

        Pagination is also supported using the `first` and `max` parameters.

        For the complete list of supported query parameters, please
        refer to the Keycloak API documentation.
        """
        return get_users(self.keycloak_admin_client, as_objects=as_objects, **query_params)

    def get_user(self, id: str) -> User:
        """Returns the user representation for a given user id."""
        return get_user(self.keycloak_admin_client, id)

    def create_user(self, user: User, as_objects=True) -> User:
        """Create a new user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
            as_objects (bool, optional): Defaults to True.
        """
        return create_user(self.keycloak_admin_client, user, as_objects=as_objects)

    def update_user(self, user: User, as_objects=True) -> User:
        """Modify an existing user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
            as_objects (bool, optional): Defaults to True.
        """
        return update_user(self.keycloak_admin_client, user, as_objects=as_objects)

    def delete_user(self, user: User) -> None:
        """Delete an existing user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
        """
        return self.keycloak_admin_client.delete_user(user.id)


def _admin_client(client):

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


def get_users(admin_client: KeycloakAdmin, as_objects=True, **query_params):

    users = admin_client.get_users(query=query_params)
    for user in users:
        _add_group_and_roles(admin_client, user)

    if not as_objects:
        return users

    # force admin check
    for user in users:
        user["is_admin"] = user

    schema = UserSchema(many=True)
    return schema.load(users)


def get_user(admin_client: KeycloakAdmin, id: str, as_objects=True):

    user = admin_client.get_user(user_id=id)
    _add_group_and_roles(admin_client, user)

    if not as_objects:
        return user

    # force admin check
    user["is_admin"] = user

    schema = UserSchema(many=False)
    return schema.load(user)


def _add_group_and_roles(admin_client: KeycloakAdmin, user: dict):
    uid = user["id"]

    # query groups
    groups = admin_client.get_user_groups(uid)
    user["groups"] = [g["name"] for g in groups]

    # query roles
    realm_roles = admin_client.get_realm_roles_of_user(uid)
    user["realm_roles"] = [r["name"] for r in realm_roles]


def create_user(admin_client: KeycloakAdmin, user: User, as_objects=True):
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

    uid = admin_client.create_user(data)
    return get_user(admin_client, uid, as_objects)


def update_user(admin_client: KeycloakAdmin, user: User, as_objects=True):
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

    data = admin_client.update_user(user.id, data)

    if not as_objects:
        return data

    user = schema.load(data)
    return user
