# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri, O.Koenig
# ----------------------------------------------------------

import logging

from .auth.authenticate import authenticate
from .connection import create_session
from .exceptions import raise_for_status

log = logging.getLogger(__name__)


class Client(object):
    """A python interface to the Remote Execution Platform (REP) API.

    Uses the provided credentials to create and store
    an authorized :class:`requests.Session` object.

    The following authentication workflows are supported:

        1. Access token: no authentication needed.
        2. Personal Access Token (PAT): no authentication needed.
        3. Username and password: the client connects to the OAuth server and
          requests access and refresh tokens.
        4. Refresh token: the client connects to the OAuth server and
          requests a new access token.

    These alternative workflows are evaluated in the order listed above.

    Parameters
    ----------
    rep_url : str
        The base path for the server to call, e.g. "https://localhost:8443/rep".
    username : str, optional
        Username
    password : str, optional
        Password
    refresh_token : str, optional
        Refresh Token
    access_token : str, optional
        Access Token
    pat: str, optional
        Personal Access Token

    Examples
    --------
    Create client object and connect to REP with username and password

    >>> from ansys.rep.client import Client
    >>> cl = Client(
            rep_url="https://localhost:8443/rep", username="repadmin", password="repadmin"
        )

    Create client object and connect to REP with a PAT

    >>> cl = Client(
        rep_url="https://localhost:8443/rep",
        pat="stalHBSPyb4k5PVVsGUVHC1KKDvi0jIRL3gFKTy6wC4FcOeWv8"
    )

    Create client object and connect to REP with refresh token

    >>> cl = Client(
        rep_url="https://localhost:8443/rep",
        username="repadmin",
        refresh_token="eyJhbGciOiJIUzI1NiIsInR5cC..."
    )

    """

    def __init__(
        self,
        rep_url: str = "https://localhost:8443/rep",
        username: str = None,
        password: str = None,
        *,
        realm: str = "rep",
        grant_type: str = "password",
        scope="openid",
        client_id: str = "rep-cli",
        client_secret: str = None,
        access_token: str = None,
        refresh_token: str = None,
        pat: str = None,
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
        self.access_token = None
        self.pat = None

        if access_token:
            log.debug("Authenticate with access token")
            self.access_token = access_token
        elif pat:
            self.pat = pat
            log.debug("Authenticate with PAT")
        else:
            if not password and refresh_token:
                grant_type = "refresh_token"
                log.debug("Authenticate with refresh token")
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

        self.session = create_session(self.access_token, self.pat)
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
            and self.refresh_token is not None
        ):
            log.info(f"401 authorization error: trying to get a new access token.")
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
        tokens = authenticate(
            url=self.auth_url or self.rep_url,
            refresh_token=self.refresh_token,
            username=self.username,
            grant_type="refresh_token",
        )
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        self.session.headers.update({"Authorization": "Bearer %s" % tokens["access_token"]})
