# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri O.Koenig
# ----------------------------------------------------------
import logging
import urllib.parse

import requests

from ..exceptions import raise_for_status

log = logging.getLogger(__name__)


def get_oidc_response(
    server_url: str,
    *,
    grant_type: str,
    client_id: str,
    client_secret: str = None,
    username: str = None,
    password: str = None,
    realm: str = "rep",
    scope="openid",
    refresh_token=None,
    timeout=10,
):
    session = requests.Session()
    session.verify = False
    session.headers = ({"content-type": "application/x-www-form-urlencoded"},)

    path = f"auth/realms/{realm}"
    if path in server_url:
        auth_url = server_url
    else:
        auth_url = f"{server_url}/{path}"
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

    log.debug(
        f"Retrieving access token for client {client_id} from {auth_url} using {grant_type} grant"
    )
    r = session.post(token_url, data=data, timeout=timeout)

    if r.status_code != 200:
        raise RuntimeError(
            f"""Failed to retrieve access token for client {client_id} from {token_url}
            using {grant_type} grant, status code {r.status_code}: {r.content.decode()}"""
        )

    return r.json()


def authenticate(
    url: str = "https://localhost:8443/rep",
    realm: str = "rep",
    grant_type: str = "password",
    scope="openid",
    client_id: str = "rep-cli",
    client_secret: str = None,
    username: str = "repadmin",
    password: str = "repadmin",
    refresh_token: str = None,
    timeout: float = 10.0,
):
    """
    Authenticate user with either password or refresh token against REP authentication service.
    If successful, the response includes access and refresh tokens.

    Args:
        url (str): The base path for the server to call, e.g. "https://localhost:8443/rep".
        username (str): Username
        password (str): Password
        refresh_token (str, optional): Refresh token.
        timeout (float, optional): Timeout in seconds. Defaults to 10.
        scope (str, optional): String containing one or more requested scopes.
                               Defaults to 'openid'.
        client_id (str, optional): The client type. Defaults to 'rep-cli'.

    Returns:
        dict: JSON-encoded content of a :class:`requests.Response`
    """

    auth_postfix = f"auth/realms/{realm}"
    if url.endswith(f"/{auth_postfix}") or url.endswith(f"/{auth_postfix}/"):
        auth_url = url
    else:
        auth_url = urllib.parse.urljoin(url + "/", auth_postfix)
    log.debug(f"Authenticating using {auth_url}")

    session = requests.Session()
    session.verify = False
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

    log.debug(
        f"Retrieving access token for client {client_id} from {auth_url} using {grant_type} grant"
    )
    r = session.post(token_url, data=data, timeout=timeout)

    raise_for_status(r)
    return r.json()


def generate_personal_access_token(session: requests.Session, url: str):
    """
    Generate PAT from auth service

    Parameters
    ----------
    session : :class:`requests.Session`
        An authenticated REP session with a valid access token.
    url : str
        REP url, e.g. "https://localhost:8443/rep".
    """
    r = session.get(f"{url}/auth/realms/rep/verify-pat/token")
    raise_for_status(r)
    return r.text


def get_personal_access_token_info(session: requests.Session, url: str):

    r = session.get(f"{url}/auth/realms/rep/verify-pat/hasToken")
    raise_for_status(r)
    return r.json()
