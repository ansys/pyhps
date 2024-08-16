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
"""Module providing the Python client to the HPS APIs."""

import logging
from typing import Union
import warnings

import jwt
import requests

from .authenticate import authenticate
from .connection import create_session
from .exceptions import HPSError, raise_for_status
from .warnings import UnverifiedHTTPSRequestsWarning

log = logging.getLogger(__name__)


class Client(object):
    """Provides the Python client to the HPS APIs.

    This class uses the provided credentials to create and store
    an authorized :class:`requests.Session` object.

    The following alternative authentication workflows are supported
    and evaluated in the order listed:

    - Access token: No authentication is needed.
    - Username and password: The client connects to the OAuth server and
      requests access and refresh tokens.
    - Refresh token: The client connects to the OAuth server and
      requests a new access token.
    - Client credentials: The client authenticates with the ``client_id`` and ``client_secret``
      parameters to obtain a new access token. (A refresh token is not included.)

    Parameters
    ----------
    url : str
        Base path for the server to call. The default is ``'https://127.0.0.1:8443/hps'``.
    username : str, optional
        Username.
    password : str, optional
        Password.
    realm : str, optional
        Keycloak realm. The default is ``'rep'``.
    grant_type : str, optional
        Authentication method. The default is ``'password'``.
    scope : str, optional
        String containing one or more requested scopes. The default is ``'openid'``.
    client_id : str, optional
        Client type. The default is ``'rep-cli'``.
    client_secret : str, optional
        Client secret. The default is ``None``.
    access_token : str, optional
        Access token.
    refresh_token : str, optional
        Refresh token.
    auth_url : str, optional
    all_fields : bool, optional
        Whether to apply the ``fields="all"`` query parameter to all requests so
        that all available fields are returned for the requested resources. The
        default is ``True``.
    verify : Union[bool, str], optional
        If a Boolean, whether to verify the server's TLS certificate. The default
        is ``None`, which disables certificate validation and warns the user about it.
        If a string, the path to the CA bundle to use. For more information,
        see the :class:`requests.Session` documentation.
    disable_security_warnings : bool, optional
        Whether to disable urllib3 warnings about insecure HTTPS requests. The default is ``True``.
        For more information, see urllib3 documentation about TLS warnings.

    Examples
    --------

    Create a client object and connect to HPS with a username and password.

    >>> from ansys.hps.client import Client
    >>> cl = Client(
    ...     url="https://localhost:8443/hps",
    ...     username="repuser",
    ...     password="repuser"
    ... )

    Create a client object and connect to HPS with a refresh token.

    >>> cl = Client(
    ...     url="https://localhost:8443/hps",
    ...     username="repuser",
    ...     refresh_token="eyJhbGciOiJIUzI1NiIsInR5cC..."
    >>> )

    """

    def __init__(
        self,
        url: str = "https://127.0.0.1:8443/hps",
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
        all_fields=True,
        verify: Union[bool, str] = None,
        disable_security_warnings: bool = True,
        **kwargs,
    ):

        rep_url = kwargs.get("rep_url", None)
        if rep_url is not None:
            url = rep_url
            msg = "The 'rep_url' input argument is deprecated. Use 'url' instead."
            warnings.warn(msg, DeprecationWarning)
            log.warning(msg)

        auth_url = kwargs.get("auth_url", None)
        if auth_url is not None:
            msg = (
                "The 'auth_url' input argument is deprecated. Use None instead. "
                "New HPS deployments will determine this automatically."
            )
            warnings.warn(msg, DeprecationWarning)
            log.warning(msg)

        self.url = url
        self.access_token = None
        self.refresh_token = None
        self.username = username
        self.realm = realm
        self.grant_type = grant_type
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        self.verify = verify

        if self.verify is None:
            self.verify = False
            msg = (
                f"Certificate verification is disabled. "
                f"Unverified HTTPS requests are made to {self.url}."
            )
            warnings.warn(msg, UnverifiedHTTPSRequestsWarning)
            log.warning(msg)

        if disable_security_warnings:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning
            )

        self.auth_url = auth_url

        if not auth_url:
            with requests.session() as session:
                session.verify = self.verify
                jms_info_url = url.rstrip("/") + "/jms/api/v1"
                resp = session.get(jms_info_url)
                if resp.status_code != 200:
                    raise RuntimeError(
                        f"Failed to contact jms info endpoint {jms_info_url}, \
                            status code {resp.status_code}: {resp.content.decode()}"
                    )
                else:
                    jms_data = resp.json()
                    if "services" in jms_data and "external_auth_url" in jms_data["services"]:
                        self.auth_url = resp.json()["services"]["external_auth_url"]
                    else:
                        log.warning(
                            "Legacy JMS service does not include external_auth_url. \
                                Generating auth_url..."
                        )
                        if realm:
                            self.auth_url = f"{url.rstrip('/')}/auth/realms/{realm}"

        if access_token:
            log.debug("Authenticate with access token")
            self.access_token = access_token
        else:
            if username and password:
                self.grant_type = "password"
            elif refresh_token:
                self.grant_type = "refresh_token"
            elif client_secret:
                self.grant_type = "client_credentials"

            log.debug(f"Authenticating with '{self.grant_type}' grant type.")

            tokens = authenticate(
                auth_url=self.auth_url,
                grant_type=self.grant_type,
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                refresh_token=refresh_token,
                verify=self.verify,
            )
            self.access_token = tokens["access_token"]
            # client credentials flow does not return a refresh token
            self.refresh_token = tokens.get("refresh_token", None)

        parsed_username = None
        token = {}
        try:
            token = jwt.decode(self.access_token, options={"verify_signature": False})
        except Exception:
            raise HPSError("Authentication token was invalid.")

        # Try to get the standard keycloak name, then other possible valid names
        parsed_username = self._get_username(token)

        if parsed_username is not None:
            if self.username is not None and self.username != parsed_username:
                raise HPSError(
                    (
                        f"Username: '{self.username}' and "
                        f"preferred_username: '{parsed_username}' "
                        "from access token do not match."
                    )
                )
            self.username = parsed_username

        self.session = create_session(
            self.access_token,
            verify=self.verify,
        )
        if all_fields:
            self.session.params = {"fields": "all"}

        # register hook to handle expiring of the refresh token
        self.session.hooks["response"] = [self._auto_refresh_token, raise_for_status]
        self._unauthorized_num_retry = 0
        self._unauthorized_max_retry = 1

    def _get_username(self, decoded_token):
        parsed_username = decoded_token.get("preferred_username", None)
        if not parsed_username:
            parsed_username = decoded_token.get("username", None)
        if not parsed_username:
            parsed_username = decoded_token.get("name", None)

        # Service accounts look like "aud -> service_client_id"
        if not parsed_username:
            if decoded_token.get("oid", "oid_not_found") == decoded_token.get(
                "sub", "sub_not_found"
            ):
                parsed_username = "service_account_" + decoded_token.get("aud", "aud_not_set")
            else:
                raise HPSError("Authentication token had no username.")
        return parsed_username

    @property
    def rep_url(self) -> str:
        msg = "The client 'rep_url' property is deprecated. Use 'url' instead."
        warnings.warn(msg, DeprecationWarning)
        log.warning(msg)
        return self.url

    @property
    def auth_api_url(self) -> str:
        msg = f"The client 'auth_api_url' property is deprecated. \
               There is no generic auth_api exposed."
        warnings.warn(msg, DeprecationWarning)
        log.warning(msg)
        auth_api_base, sep, _ = self.auth_url.partition("realms")
        if sep:
            return auth_api_base
        else:
            log.error("auth_api not valid for non-keycloak implementation")
            return None

    def _auto_refresh_token(self, response, *args, **kwargs):
        """Automatically refreshes the access token and
        resends the request in case of an unauthorized error."""
        if (
            response.status_code == 401
            and self._unauthorized_num_retry < self._unauthorized_max_retry
        ):
            log.info(f"401 authorization error: Trying to get a new access token.")
            self._unauthorized_num_retry += 1
            self.refresh_access_token()
            response.request.headers.update(
                {"Authorization": self.session.headers["Authorization"]}
            )
            log.debug(f"Retrying request with updated access token.")
            return self.session.send(response.request)

        self._unauthorized_num_retry = 0
        return response

    def refresh_access_token(self):
        """Request a new access token"""
        if self.grant_type == "client_credentials":
            # Its not recommended to give refresh tokens to client_credentials grant types
            # as per OAuth 2.0 RFC6749 Section 4.4.3, so handle these specially...
            tokens = authenticate(
                auth_url=self.auth_url,
                grant_type="client_credentials",
                scope=self.scope,
                client_id=self.client_id,
                client_secret=self.client_secret,
                verify=self.verify,
            )
        else:
            # Other workflows for authentication generally support refresh_tokens
            tokens = authenticate(
                auth_url=self.auth_url,
                grant_type="refresh_token",
                scope=self.scope,
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                refresh_token=self.refresh_token,
                verify=self.verify,
            )
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens.get("refresh_token", None)
        self.session.headers.update({"Authorization": "Bearer %s" % tokens["access_token"]})
