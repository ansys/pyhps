# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri, O.Koenig
# ----------------------------------------------------------

from ansys.rep.client.connection import create_session

from ..exceptions import raise_for_status
from .authenticate import authenticate
from .resource.user import create_user, delete_user, get_users, update_user


class Client(object):
    """A python interface to the Authorization Service API.

    Users with admin rights (such as the default ``repadmin`` user) can create new
    users as well as modify or delete existing ones. Non-admin users are only allowed
    to query the list of exisiting users.

    Args:
        rep_url (str): The base path for the server to call, e.g. "https://127.0.0.1/dcs".
        username (str): Username
        password (str): Password

    Example:

        >>> from ansys.rep.client.auth import Client, User
        >>> cl = Client(rep_url="https://127.0.0.1/dcs/", username="repadmin", password="repadmin")
        >>> existing_users = cl.get_users()
        >>> new_user = User(username='test_user', password='dummy',
        >>>                 email='test_user@test.com', fullname='Test User',
        >>>                 is_admin=False)
        >>> cl.create_user(new_user)

    """

    def __init__(
        self,
        rep_url,
        *,
        realm: str = "rep",
        username: str = "repadmin",
        password: str = "repadmin",
        grant_type: str = "password",
        scope="openid",
        client_id: str = "rep-cli",
        client_secret: str = None,
    ):

        self.rep_url = rep_url
        self.auth_api_url = self.rep_url + f"/auth/"

        self.username = username
        self.password = password
        self.realm = realm
        self.grant_type = grant_type
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret

        tokens = authenticate(
            url=self.rep_url,
            realm=realm,
            grant_type=grant_type,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        )
        self.access_token = tokens["access_token"]

        self.session = create_session(self.access_token)
        self.session.headers["content-type"] = "application/json"

        # register hook to handle expiring of the refresh token
        self.session.hooks["response"] = [raise_for_status]

    # def get_api_info(self):
    #     """Return info like version, build date etc of the Auth API the client is connected to."""
    #     r = self.session.get(self.auth_api_url)
    #     return r.json()

    def get_users(self, as_objects=True):
        """Return a list of users."""
        return get_users(self, as_objects=as_objects)

    def create_user(self, user, as_objects=True):
        """Create a new user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
            as_objects (bool, optional): Defaults to True.
        """
        return create_user(self, user, as_objects=as_objects)

    def update_user(self, user, as_objects=True):
        """Modify an existing user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
            as_objects (bool, optional): Defaults to True.
        """
        return update_user(self, user, as_objects=as_objects)

    def delete_user(self, user):
        """Delete an existing user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
        """
        return delete_user(self, user)
