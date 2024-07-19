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
"""Module that provides authentication for the user with a password or refresh token against the
HPS authentication service."""
import logging
from typing import Union, List

import requests

from .exceptions import raise_for_status

log = logging.getLogger(__name__)

OIDC_DISCOVERY_ENDPOINT_PATH = "/.well-known/openid-configuration"

class Discovered:
    keys: List[dict]
    algorithms: List[str]
    openid_config: dict
    claims_supported: List[str]

    def __init__(self, keys, algorithms, openid_config, claims_supported=[]):
        self.keys = keys
        self.algorithms = algorithms
        self.openid_config = openid_config
        self.claims_supported = claims_supported

    # After we grab the standard keys from the Identity Provider, add in any local keys we support...
    def add_keys(self, addtl_jwks_keys):
        self.keys.extend(addtl_jwks_keys)


def get_discovery_data(auth_url: str, timeout: int = 10) -> dict:
    """
    Caching this discovery data because it should not change except when restarting OIDC services or adding new routes
    """
    disco_url = auth_url.rstrip("/") + OIDC_DISCOVERY_ENDPOINT_PATH
    log.trace(f"Discovery URL: {disco_url}")
    with requests.Session() as session:
        session.verify = False
        disco = session.get(disco_url, timeout=timeout)
        if disco.status_code != 200:
            raise RuntimeError(
                f"Failed to contact discovery endpoint {disco_url}, \
                    status code {disco.status_code}: {disco.content.decode()}"
            )

        return disco.json()

def authenticate(
    auth_url: str = "https://127.0.0.1:8443/hps/auth/realms/rep",
    grant_type: str = "password",
    scope="openid",
    client_id: str = "rep-cli",
    client_secret: str = None,
    username: str = None,
    password: str = None,
    refresh_token: str = None,
    timeout: float = 10.0,
    verify: Union[bool, str] = True,
    **kwargs,
):
    """
    Authenticates the user with a password or refresh token against the HPS authentication service.

    If this method is successful, the response includes access and refresh tokens.

    Parameters
    ----------

    url : str, optional
        Base path for the server to call. The default is ``'https://127.0.0.1:8443/rep'``.
    realm : str, optional
        Keycloak realm. The default is ``'rep'``.
    grant_type: str, optional
        Authentication method. The default is ``'password'``.
    scope : str, optional
        String containing one or more requested scopes. The default is ``'openid'``.
    client_id : str, optional
        Client type. The default is ``'rep-cli'``.
    client_secret : str, optional
        Client secret. The default is ``None``.
    username : str, optional
        Username.
    password : str, optional.
        Password.
    refresh_token : str, optional
        Refresh token.
    timeout : float, optional
        Timeout in seconds. The default is ``10.0``.
    verify: Union[bool, str], optional
        If a Boolean, whether to verify the server's TLS certificate. If a string, the
        path to the CA bundle to use. For more information, see the :class:`requests.Session`
        documentation.

    Returns
    -------
    dict
        JSON-encoded content of a :class:`requests.Response` object.
    """

    auth_url = str(auth_url)
    disco_dict = get_discovery_data(auth_url, timeout)
    token_url = disco_dict["token_endpoint"]

    with requests.Session() as session:
        session.verify = False
        session.headers = ({"content-type": "application/x-www-form-urlencoded"},)

        # seemingly necessary all the time
        data = {
            "client_id": client_id,
            "scope": scope,
        }

        # If someone specifically calls out a grant type, just use it directly.
        if grant_type and not grant_type.isspace():
            data["grant_type"] = grant_type

        # Many grant types can have client secrets, client secret with other things just means it not a public endpoint
        if client_secret is not None and not client_secret.isspace():
            data["client_secret"] = client_secret

        # Username is also used in more than one workflow.
        if username and not username.isspace():
            data["username"] = username

        # If password and username, and its not already defined, this has to be password grant
        if password and not password.isspace():
            data["password"] = password
            if "username" in data and not "grant_type" in data:
                data["grant_type"] = "password"

        # If a refresh token is provided, the grant type is refresh token unless otherwise listed.
        if refresh_token and not refresh_token.isspace():
            data["refresh_token"] = refresh_token
            if not "grant_type" in data:
                data["grant_type"] = "refresh_token"

        # If we have a secret and no other grant types have been suggested, then it must be a simple client_creds
        if "client_secret" in data and not "grant_type" in data:
            data["grant_type"] = "client_credentials"

        log.debug(
            f"Retrieving access token for client {client_id} from {auth_url} using {grant_type} grant."
        )

        r = session.post(token_url, data=data, timeout=timeout)

        raise_for_status(r)
        return r.json()
