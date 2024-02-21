# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module providing the Python interface to the Authorization Service API."""

from typing import List

from keycloak import KeycloakAdmin

from ..resource import User
from ..schema.user import UserSchema


class AuthApi:
    """Provides the Python interface to the Authorization Service API.

    Admin users with the Keycloak "manage-users" role can create
    users as well as modify or delete existing users. Non-admin users are only allowed
    to query the list of existing users.

    Parameters
    ----------
    client : Client
        HPS client object.

    Examples
    --------

    Get users whose first name contains ``john``.

    >>> from ansys.hps.client import Client
    >>> from ansys.hps.client.auth import AuthApi, User
    >>> cl = Client(
    ...     url="https://127.0.0.1:8443/hps", username="repuser", password="repuser"
    ... )
    >>> auth_api = AuthApi(cl)
    >>> users = auth_api.get_users(firstName="john", exact=False)

    Create a user:

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
        """API URL."""
        return f"{self.client.url}/auth/"

    @property
    def keycloak_admin_client(self) -> KeycloakAdmin:
        """Authenticated client for the Keycloak Admin API."""
        return _admin_client(self.client)

    def get_users(self, as_objects=True, **query_params) -> List[User]:
        """Get users, filtered according to query parameters.

        Examples of query parameters are:
        - ``username``
        - ``firstName``
        - ``lastName``
        - ``exact``

        Pagination is also supported using the ``first`` and ``max`` parameters.

        For a list of supported query parameters, see the Keycloak API documentation.
        """
        return get_users(self.keycloak_admin_client, as_objects=as_objects, **query_params)

    def get_user(self, id: str) -> User:
        """Get the user representation for a given user ID."""
        return get_user(self.keycloak_admin_client, id)

    def get_user_groups(self, id: str) -> List[str]:
        """Get the groups that the user belongs to."""
        return [g["name"] for g in self.keycloak_admin_client.get_user_groups(id)]

    def get_user_realm_roles(self, id: str) -> List[str]:
        """Get the realm roles for the user."""
        return [r["name"] for r in self.keycloak_admin_client.get_realm_roles_of_user(id)]

    def user_is_admin(self, id: str) -> bool:
        """Determine if the user is a system administrator."""

        from ansys.hps.client.jms import JmsApi

        # the admin keys are configurable settings of JMS
        # they need to be queried, can't be hardcoded
        jms_api = JmsApi(self.client)
        admin_keys = jms_api.get_api_info()["settings"]["admin_keys"]

        # query user groups and roles and store in the same format
        # as admin keys
        user_keys = [f"groups.{name}" for name in self.get_user_groups(id)] + [
            f"roles.{name}" for name in self.get_user_realm_roles(id)
        ]

        # match admin and user keys
        if set(admin_keys).intersection(user_keys):
            return True

        return False

    def create_user(self, user: User, as_objects=True) -> User:
        """Create a user.

        Parameters
        ----------
        user : :class:`ansys.hps.client.auth.User`
            User object. The default is ``None``.
        as_objects : bool, optional
            The default is ``True``.
        """
        return create_user(self.keycloak_admin_client, user, as_objects=as_objects)

    def update_user(self, user: User, as_objects=True) -> User:
        """Modify an existing user.

        Parameters
        ----------
        user : :class:`ansys.hps.client.auth.User`
            User object. The default is ``None``.
        as_objects : bool, optional
            The default is  ``True``.
        """
        return update_user(self.keycloak_admin_client, user, as_objects=as_objects)

    def delete_user(self, user: User) -> None:
        """Delete an existing user.

        Parameters
        ----------
        user : :class:`ansys.hps.client.auth.User`
            User object. The default is ``None``.
        """
        return self.keycloak_admin_client.delete_user(user.id)


def _admin_client(client):
    """Set information for admin.

    Parameters
    ----------
    client : Client
        HPS client object.
    """
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
    """Get users as admin.

    Parameters
    ----------
    admin_client : KeycloakAdmin
        Keycloak admin user.
    """
    users = admin_client.get_users(query=query_params)

    if not as_objects:
        return users

    schema = UserSchema(many=True)
    return schema.load(users)


def get_user(admin_client: KeycloakAdmin, id: str, as_objects=True):
    """Get user using ID.

    Parameters
    ----------
    admin_client: KeycloakAdmin
        Keycloak admin user.
    id : str
        User ID.
    """
    user = admin_client.get_user(user_id=id)

    if not as_objects:
        return user

    schema = UserSchema(many=False)
    return schema.load(user)


def create_user(admin_client: KeycloakAdmin, user: User, as_objects=True):
    """Create user.

    Parameters
    ----------
    admin_client : KeycloakAdmin
        Keycloak admin user.
    user : User
        HPS user object.
    """
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
    """Update user.

    Parameters
    ----------
    admin_client : KeycloakAdmin
        Keycloak admin user.
    user : User
        HPS user object.
    """
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
