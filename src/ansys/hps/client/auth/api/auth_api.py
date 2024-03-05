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

from typing import Dict, List

from ansys.hps.client import Client

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

    def __init__(self, client: Client):
        self.client = client

    @property
    def url(self) -> str:
        """API URL."""
        return f"{self.client.url}/auth"

    @property
    def realm_url(self) -> str:
        """Realm URL."""
        return f"{self.url}/admin/realms/{self.client.realm}"

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
        r = self.client.session.get(url=f"{self.realm_url}/users", params=query_params)
        data = r.json()

        if not as_objects:
            return data

        schema = UserSchema(many=True)
        return schema.load(data)

    def get_user(self, id: str, as_object: bool = True) -> User:
        """Get the user representation for a given user ID."""
        r = self.client.session.get(
            url=f"{self.realm_url}/users/{id}",
        )
        data = r.json()
        if not as_object:
            return data

        schema = UserSchema(many=False)
        return schema.load(data)

    def get_user_groups_names(self, id: str) -> List[str]:
        """Get the name of the groups that the user belongs to."""
        return [g["name"] for g in self.get_user_groups(id)]

    def get_user_realm_roles_names(self, id: str) -> List[str]:
        """Get the name of the realm roles for the user."""
        return [r["name"] for r in self.get_user_realm_roles(id)]

    def get_user_groups(self, id: str) -> List[Dict]:
        """Get the groups that the user belongs to."""
        r = self.client.session.get(
            url=f"{self.realm_url}/users/{id}/groups",
        )
        return r.json()

    def get_user_realm_roles(self, id: str) -> List[Dict]:
        """Get the realm roles for the user."""
        r = self.client.session.get(
            url=f"{self.realm_url}/users/{id}/role-mappings/realm",
        )
        return r.json()

    # def get_composite_realm_roles_of_role(self, role_name: str) -> list[str]:
    #     r = self.client.session.get(
    #         url=f"{self.realm_url}/roles/{role_name}/composites",
    #         params={"fields": None},
    #     )
    #     return r.json()

    def user_is_admin(self, id: str) -> bool:
        """Determine if the user is a system administrator."""

        from ansys.hps.client.jms import JmsApi

        # the admin keys are configurable settings of JMS
        # they need to be queried, can't be hardcoded
        jms_api = JmsApi(self.client)
        admin_keys = jms_api.get_api_info()["settings"]["admin_keys"]

        # query user groups and roles and store in the same format
        # as admin keys
        user_keys = [f"groups.{name}" for name in self.get_user_groups_names(id)] + [
            f"roles.{name}" for name in self.get_user_realm_roles_names(id)
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

        r = self.client.session.post(
            url=f"{self.realm_url}/users",
            data=data,
        )

        _last_slash_idx = r.headers["Location"].rindex("/")  # todo rewrite
        uid = r.headers["Location"][_last_slash_idx + 1 :]
        return self.get_user(uid, as_objects)

    def update_user(self, user: User, as_objects=True) -> User:
        """Modify an existing user.

        Parameters
        ----------
        user : :class:`ansys.hps.client.auth.User`
            User object. The default is ``None``.
        as_objects : bool, optional
            The default is  ``True``.
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
        r = self.client.session.post(
            url=f"{self.realm_url}/users/{user.id}",
            data=data,
        )
        data = r.json()

        if not as_objects:
            return data

        user = schema.load(data)
        return user

    def delete_user(self, user: User) -> None:
        """Delete an existing user.

        Parameters
        ----------
        user : :class:`ansys.hps.client.auth.User`
            User object. The default is ``None``.
        """
        _ = self.client.session.delete(
            url=f"{self.realm_url}/users/{user.id}",
        )
        return
