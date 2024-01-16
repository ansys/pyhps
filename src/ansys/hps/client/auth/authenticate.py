# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri O.Koenig
# ----------------------------------------------------------
import logging
from typing import Union
import urllib.parse

import requests

from ..exceptions import raise_for_status

log = logging.getLogger(__name__)


def authenticate(
    url: str = "https://127.0.0.1:8443/rep",
    realm: str = "rep",
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
    Authenticate user with either password or refresh token against HPS authentication service.
    If successful, the response includes access and refresh tokens.

    Parameters
    ----------

    url : str
        The base path for the server to call, e.g. "https://127.0.0.1:8443/rep".
    realm : str
        Keycloak realm, defaults to 'rep'.
    grant_type: str
        Authentication method, defaults to 'password'.
    username : str
        Username
    password : str
        Password
    refresh_token : str, optional
        Refresh token.
    timeout : float, optional
        Timeout in seconds. Defaults to 10.
    scope : str, optional
        String containing one or more requested scopes. Defaults to 'openid'.
    client_id : str, optional
        The client type. Defaults to 'rep-cli'.
    client_secret : str, optional
        The client secret.
    verify: Union[bool, str], optional
        Either a boolean, in which case it controls whether we verify the
        server's TLS certificate, or a string, in which case it must be
        a path to a CA bundle to use.
        See the :class:`requests.Session` documentation.

    Returns
    ----------
    dict
        JSON-encoded content of a :class:`requests.Response`
    """

    auth_postfix = f"auth/realms/{realm}"
    if url.endswith(f"/{auth_postfix}") or url.endswith(f"/{auth_postfix}/"):
        auth_url = url
    else:
        auth_url = urllib.parse.urljoin(url + "/", auth_postfix)
    log.debug(f"Authenticating using {auth_url}")

    session = requests.Session()
    session.verify = verify
    session.headers = ({"content-type": "application/x-www-form-urlencoded"},)

    token_url = f"{auth_url}/protocol/openid-connect/token"

    data = {
        "client_id": client_id,
        "grant_type": grant_type,
        "scope": scope,
    }
    if client_secret is not None:
        data["client_secret"] = client_secret
    if username is not None:
        data["username"] = username
    if password is not None:
        data["password"] = password
    if refresh_token is not None:
        data["refresh_token"] = refresh_token

    data.update(**kwargs)

    log.debug(
        f"Retrieving access token for client {client_id} from {auth_url} using {grant_type} grant"
    )
    r = session.post(token_url, data=data, timeout=timeout)

    raise_for_status(r)
    return r.json()
