"""Script to demonstrate OIDC authentication with Authorization Code Flow using PKCE.

Mostly inspired by:
    - https://www.camiloterevinto.com/post/oauth-pkce-flow-from-python-desktop
    - https://www.stefaanlippens.net/oauth-code-flow-pkce.html
"""

import argparse
import base64
import hashlib
import os
import re
import socket
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib import parse

import requests
from requests import Request


class OAuthHttpServer(HTTPServer):
    """HTTP server for OAuth authentication with authorization code storage."""

    def __init__(self, *args, **kwargs):
        """Initialize the OAuth HTTP server.

        Args:
            *args: Variable length argument list passed to HTTPServer.
            **kwargs: Arbitrary keyword arguments passed to HTTPServer.

        """
        HTTPServer.__init__(self, *args, **kwargs)
        self.authorization_code = ""


class OAuthHttpHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth authentication callbacks."""

    def do_GET(self):
        """Handle GET requests to capture OAuth authorization code."""
        parsed = parse.urlparse(self.path)
        qs = parse.parse_qs(parsed.query)
        self.server.authorization_code = qs["code"][0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        html_body = b"""
            <html>
                <head>
                    <script type="text/javascript">
                        window.close();
                    </script>
                </head>
                <body>
                    <p>Operation successful. You can safely close this window.</p>
                </body>
            </html>
        """
        self.wfile.write(html_body)

    def log_message(self, format, *args):
        """Suppress log messages from the HTTP server."""
        return


def generate_code() -> tuple[str, str]:
    """Generate PKCE code verifier and code challenge for OAuth authentication.

    Returns:
        tuple[str, str]: A tuple containing (code_verifier, code_challenge).

    """
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")

    return code_verifier, code_challenge


def prepare_auth_url(
    auth_url: str,
    redirect_uri: str,
    code_challenge: str,
    client_id: str = "rep-cli",
    scope: str = "openid",
) -> str:
    """Prepare OAuth authorization URL with PKCE parameters.

    Args:
        auth_url: OAuth authorization endpoint URL.
        redirect_uri: Redirect URI for OAuth callback.
        code_challenge: PKCE code challenge string.
        client_id: OAuth client ID. Defaults to "rep-cli".
        scope: OAuth scope. Defaults to "openid".

    Returns:
        str: Complete authorization URL with query parameters.

    """
    return (
        Request(
            method="GET",
            url=f"{auth_url}",
            params={
                "response_type": "code",
                "client_id": client_id,
                "scope": scope,
                "redirect_uri": redirect_uri,
                "state": "unused",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
        )
        .prepare()
        .url
    )


def find_free_port() -> int:
    """Find an available port for the local HTTP server.

    Returns:
        int: An available port number.

    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def login(config: dict[str, Any]) -> tuple[str, str, str]:
    """Perform OAuth login with PKCE flow.

    Args:
        config: Configuration dictionary containing OAuth parameters including
                auth_url, client_id, scope, and token_url.

    Returns:
        tuple[str, str, str]: A tuple containing (access_token, refresh_token, id_token).

    """
    port = find_free_port()
    with OAuthHttpServer(("", port), OAuthHttpHandler) as httpd:
        # print(f"Local HTTP server available at http://localhost:{httpd.server_port}")

        code_verifier, code_challenge = generate_code()

        redirect_uri = f"http://localhost:{port}"

        auth_uri = prepare_auth_url(
            auth_url=config["auth_url"],
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            client_id=config["client_id"],
            scope=config["scope"],
        )

        webbrowser.open_new(auth_uri)

        httpd.handle_request()

        auth_code = httpd.authorization_code

        data = {
            "code": auth_code,
            "client_id": config["client_id"],
            "grant_type": "authorization_code",
            "scope": config["scope"],
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }

        response = requests.post(url=f"{config['token_url']}", data=data, verify=True)

        assert response.status_code == 200, f"Failed to login: {response.text}"

        # import json
        # print(json.dumps(response.json(), indent=2))

        access_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]
        id_token = response.json()["id_token"]

        return access_token, refresh_token, id_token


def get_config(hps_url: str) -> dict[str, Any]:
    """Retrieve OAuth configuration from HPS server.

    Args:
        hps_url: Base URL of the HPS server.

    Returns:
        dict: Configuration dictionary containing OAuth endpoints and settings.

    """
    jms_url = hps_url.rstrip("/") + "/jms/api/v1"
    response = requests.get(url=jms_url, verify=True)
    assert response.status_code == 200, f"Failed to get config from JMS: {response.text}"
    raw_config = response.json()
    config = {}
    config["base_auth_url"] = raw_config["services"]["external_auth_url"]
    config["client_id"] = raw_config["settings"]["spa_client_id"]
    config["scope"] = f"openid offline_access {raw_config['settings']['oidc_required_scope']}"

    # Get discovery
    config["disco_endpoint"] = (
        config["base_auth_url"].rstrip("/") + "/.well-known/openid-configuration"
    )

    response = requests.get(url=config["disco_endpoint"], verify=True)
    assert response.status_code == 200, (
        f"Failed to get discovery from {config['disco_endpoint']}: {response.text}"
    )
    raw_disco = response.json()
    # Fill specific endpoints from discovery
    config["auth_url"] = raw_disco["authorization_endpoint"]
    config["token_url"] = raw_disco["token_endpoint"]
    config["issuer_url"] = raw_disco["issuer"]
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default="https://hps.ansys.com/hps")

    args = parser.parse_args()

    config = get_config(args.url)
    access_token, refresh_token, id_token = login(config)
    # print(f"Successfully logged in. Access token: {access_token}")
    print(access_token)
