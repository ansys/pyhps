# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri, O.Koenig
# ----------------------------------------------------------

from .auth.authenticate import authenticate
from .connection import create_session
from .exceptions import raise_for_status


class Client(object):
    """A python interface to the Remote Execution Platform (REP) API.

    Uses the provided credentials to create and store
    an authorized :class:`requests.Session` object.

    The following authentication workflows are supported:

        - Username and password: the client connects to the OAuth server and
          requests access and refresh tokens.
        - Refresh token: the client connects to the OAuth server and
          requests a new access token.
        - Access token: no authentication needed.

    Parameters
    ----------
    rep_url : str
        The base path for the server to call, e.g. "https://127.0.0.1:8443/rep".
    username : str, optional
        Username
    password : str, optional
        Password
    refresh_token : str, optional
        Refresh Token
    access_token : str, optional
        Access Token

    Examples
    --------

    >>> from ansys.rep.client import Client
    >>> # Create client object and connect to REP with username & password
    >>> cl = Client(
            rep_url="https://localhost:8443/rep", username="repadmin", password="repadmin"
        )
    >>> # Extract refresh token to eventually store it
    >>> refresh_token = cl.refresh_token
    >>> # Alternative: Create client object and connect to REP with refresh token
    >>> cl = Client(rep_url="https://localhost:8443/rep", refresh_token=refresh_token)

    """

    def __init__(
        self,
        rep_url: str = "https://127.0.0.1:8443/rep",
        username: str = "repadmin",
        password: str = "repadmin",
        *,
        realm: str = "rep",
        grant_type: str = "password",
        scope="openid",
        client_id: str = "rep-cli",
        client_secret: str = None,
        access_token: str = None,
        refresh_token: str = None,
        auth_url: str = None,
    ):

        self.rep_url = rep_url
        self.auth_url = auth_url
        self.auth_api_url = (auth_url or rep_url) + f"/auth/"
        self.refresh_token = None
        self.username = username
        self.realm = realm
        self.grant_type = grant_type
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret

        if access_token:
            self.access_token = access_token
        else:
            tokens = authenticate(
                url=auth_url or rep_url,
                realm=realm,
                grant_type=grant_type,
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                refresh_token=refresh_token,
            )
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]

        self.session = create_session(self.access_token)
        # register hook to handle expiring of the refresh token
        self.session.hooks["response"] = [self._auto_refresh_token, raise_for_status]
        self._unauthorized_num_retry = 0
        self._unauthorized_max_retry = 1

    def _auto_refresh_token(self, response, *args, **kwargs):
        """Hook function to automatically refresh the access token and
        re-send the request in case of unauthorized error"""
        if (
            response.status_code == 401
            and self._unauthorized_num_retry < self._unauthorized_max_retry
        ):
            self._unauthorized_num_retry += 1
            self.refresh_access_token()
            response.request.headers.update(
                {"Authorization": self.session.headers["Authorization"]}
            )
            return self.session.send(response.request)

        self._unauthorized_num_retry = 0
        return response

    def refresh_access_token(self):
        """Use the refresh token to obtain a new access token"""
        tokens = authenticate(url=self.auth_url or self.rep_url, refresh_token=self.refresh_token)
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        self.session.headers.update({"Authorization": "Bearer %s" % tokens["access_token"]})
