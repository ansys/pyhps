# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri, O.Koenig
# ----------------------------------------------------------

from ..resource.user import create_user, delete_user, get_users, update_user


class AuthApi:
    """A python interface to the Authorization Service API.

    Users with admin rights (such as the default ``repadmin`` user) can create new
    users as well as modify or delete existing ones. Non-admin users are only allowed
    to query the list of existing users.

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

    def __init__(self, client):
        self.client = client

    @property
    def url(self):
        return f"{self.client.rep_url}/auth/"

    def get_users(self, as_objects=True):
        """Return a list of users."""
        return get_users(self.client, as_objects=as_objects)

    def create_user(self, user, as_objects=True):
        """Create a new user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
            as_objects (bool, optional): Defaults to True.
        """
        return create_user(self.client, user, as_objects=as_objects)

    def update_user(self, user, as_objects=True):
        """Modify an existing user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
            as_objects (bool, optional): Defaults to True.
        """
        return update_user(self.client, user, as_objects=as_objects)

    def delete_user(self, user):
        """Delete an existing user.

        Args:
            user (:class:`ansys.rep.client.auth.User`): A User object. Defaults to None.
        """
        return delete_user(self.client, user)
