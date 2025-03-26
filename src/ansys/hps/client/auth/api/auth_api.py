# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.hps.client.client import Client

from ..resource import User
from ..schema.user import UserSchema


class AuthApi:
    """Provides a minimal wrapper around the Keycloak API to query user information.

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

    """

    def __init__(self, client: Client):
        """Initialize the AuthApi object."""
        self.client = client

    @property
    def url(self) -> str:
        """API URL."""
        return f"{self.client.url}/auth"

    @property
    def realm_url(self) -> str:
        """Realm URL."""
        return f"{self.url}/admin/realms/{self.client.realm}"

    def get_users(self, as_objects=True, **query_params) -> list[User]:
        """Get users, filtered according to query parameters.

        Examples of query parameters are:

        - ``username``
        - ``firstName``
        - ``lastName``
        - ``exact``

        Pagination is also supported using the ``first`` and ``max`` parameters.

        For a list of supported query parameters, see the
        `Keycloak API documentation <https://www.keycloak.org/documentation>`__.

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

    def get_user_groups_names(self, id: str) -> list[str]:
        """Get the name of the groups that the user belongs to."""
        return [g["name"] for g in self.get_user_groups(id)]

    def get_user_realm_roles_names(self, id: str) -> list[str]:
        """Get the name of the realm roles for the user."""
        return [r["name"] for r in self.get_user_realm_roles(id)]

    def get_user_groups(self, id: str) -> list[dict]:
        """Get the groups that the user belongs to."""
        r = self.client.session.get(
            url=f"{self.realm_url}/users/{id}/groups",
        )
        return r.json()

    def get_user_realm_roles(self, id: str) -> list[dict]:
        """Get the realm roles for the user."""
        r = self.client.session.get(
            url=f"{self.realm_url}/users/{id}/role-mappings/realm",
        )
        return r.json()

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
