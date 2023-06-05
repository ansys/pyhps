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
        2. Username and password: the client connects to the OAuth server and
           requests access and refresh tokens.
        3. Refresh token: the client connects to the OAuth server and
          requests a new access token.
        4. Client credentials: authenticate with client_id and client_secret to
          obtain a new access token (a refresh token is not included).

    These alternative workflows are evaluated in the order listed above.

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
    all_fields: bool, optional
        If True, the query parameter ``fields="all"`` is applied by default
        to all requests, so that all available fields are returned for
        the requested resources.

    Examples
    --------

    Create client object and connect to REP with username and password

    >>> from ansys.rep.client import Client
    >>> cl = Client(
    ...     rep_url="https://localhost:8443/rep", username="repuser", password="repuser"
    ... )

    Create client object and connect to REP with refresh token

    >>> cl = Client(
    ...     rep_url="https://localhost:8443/rep",
    ...     username="repuser",
    ...     refresh_token="eyJhbGciOiJIUzI1NiIsInR5cC..."
    >>> )

    """

    def __init__(
        self,
        rep_url: str = "https://127.0.0.1:8443/rep",
        username: str = None,
        password: str = None,
        *,
        realm: str = "rep",
        grant_type: str = None,
        scope="openid",
        client_id: str = "rep-cli",
        client_secret: str = None,
        access_token: str = None,
        refresh_token: str = None,
        auth_url: str = None,
        all_fields=True,
    ):

        self.rep_url = rep_url
        self.auth_url = auth_url
        self.auth_api_url = (auth_url or rep_url) + f"/auth/"
        self.access_token = None
        self.refresh_token = None
        self.username = username
        self.realm = realm
        self.grant_type = grant_type
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret

        if access_token:
            log.debug("Authenticate with access token")
            self.access_token = access_token
        else:
            if username and password:
                self.grant_type = "password"
                log.debug("Authenticating with username and password")
            elif refresh_token:
                self.grant_type = "refresh_token"
                log.debug("Authenticating with refresh token")
            elif client_secret:
                self.grant_type = "client_credentials"
                log.debug("Authenticating with client credentials")

            tokens = authenticate(
                url=auth_url or rep_url,
                realm=realm,
                grant_type=self.grant_type,
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                refresh_token=refresh_token,
            )
            self.access_token = tokens["access_token"]
            # client credentials flow does not return a refresh token
            self.refresh_token = tokens.get("refresh_token", None)

        self.session = create_session(self.access_token)
        if all_fields:
            self.session.params = {"fields": "all"}

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
        """Request a new access token"""
        if self.grant_type == "client_credentials":
            tokens = authenticate(
                url=self.auth_url or self.rep_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                grant_type=self.grant_type,
            )
        else:
            tokens = authenticate(
                url=self.auth_url or self.rep_url,
                refresh_token=self.refresh_token,
                username=self.username,
                grant_type="refresh_token",
            )
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens.get("refresh_token", None)
        self.session.headers.update({"Authorization": "Bearer %s" % tokens["access_token"]})
