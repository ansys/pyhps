# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""OIDC Authorization Code + PKCE login and token persistence utilities.

Starts a temporary localhost HTTP server, opens your browser at the
login page, and exchanges the authorization code for tokens.
No password is ever entered in the terminal.

Usage
-----
    uv run python oidc_login.py --url https://localhost:8443/hps

Token Storage Security:
  - keyring (preferred): System credential manager
    - Windows: Credential Manager
    - macOS: Keychain
    - Linux: Secret Service (via python-keyring)
  - disk:
    - Windows: ``%USERPROFILE%\\.ansys\\hps_tokens.json`` (encrypted with DPAPI)
    - Unix/Linux: ``~/.ansys/hps_tokens.json`` (file permissions 0o600)
  - memory (default): Tokens kept in memory only, not persisted

Tokens can be consumed by any script that reads them.

Public Functions
----------------
browser_login(hps_url, open_browser=True, issuer=None)
    Run OIDC Authorization Code + PKCE flow and return token dict.
    Opens browser for login unless open_browser=False.

load_tokens(storage="keyring", service_name=None)
    Load saved tokens from the explicitly selected storage backend.
    For keyring loads, uses ``service_name`` or
    ``HPS_OIDC_KEYRING_SERVICE_NAME`` to select the keyring namespace.
    Returns None if no tokens found.

save_tokens(tokens, hps_url, storage="memory", service_name=None)
    Persist tokens to specified location (memory, disk, or keyring).
    Validates token schema before persistence.
    Returns path if saved to disk, otherwise None.

refresh_tokens(hps_url=None, issuer=None)
    Refresh saved tokens using refresh_token grant.
    Returns updated token dict or None if refresh fails.
"""

import argparse
import base64
import hashlib
import http.server
import os
import platform
import secrets
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests  # noqa: E402

from ...common import token_storage as _token_storage

TOKEN_FILE = _token_storage.TOKEN_FILE
CLIENT_ID = "rep-cli"
REALM = "rep"
REDIRECT_PORT = 19876
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
DEFAULT_KEYRING_SERVICE_NAME = _token_storage.DEFAULT_KEYRING_SERVICE_NAME
KEYRING_SERVICE_ENV_VAR = _token_storage.KEYRING_SERVICE_ENV_VAR


def _load_from_disk() -> dict | None:
    """Load tokens from disk file.

    Returns token dict if available, None if file doesn't exist or can't be read.
    """
    _token_storage.TOKEN_FILE = TOKEN_FILE
    return _token_storage._load_from_disk()


def load_tokens(storage: str = "keyring", service_name: str | None = None) -> dict | None:
    """Load saved tokens from the explicitly selected backend.

    Parameters
    ----------
    storage:
        Backend to load from. Supported values are ``"memory"``, ``"disk"``,
        and ``"keyring"``.
    service_name:
        Keyring service name override. Used only when ``storage="keyring"``.

    Loaded payloads are validated and normalized before being returned.

    Returns token dict if available, None if no tokens found or errors occur.

    """
    _token_storage.TOKEN_FILE = TOKEN_FILE
    return _token_storage.load_tokens(storage=storage, service_name=service_name)


def _check_keyring_backend() -> str | None:
    """Return error details if keyring backend is unavailable, else None."""
    return _token_storage._check_keyring_backend()


def _check_disk_storage_backend() -> str | None:
    """Return error details if disk storage backend is unavailable, else None."""
    _token_storage.TOKEN_FILE = TOKEN_FILE
    return _token_storage._check_disk_storage_backend()


def _check_storage_backend(storage: str) -> str | None:
    """Return error details if storage backend is unavailable, else None."""
    _token_storage.TOKEN_FILE = TOKEN_FILE
    return _token_storage._check_storage_backend(storage)


def _is_token_expired(tokens: dict, buffer_seconds: int = 60) -> bool:
    """Check if access token is expired or close to expiry.

    Parameters
    ----------
    tokens:
        Token dict with 'expires_in' and 'saved_at' fields.
    buffer_seconds:
        Seconds before actual expiry to consider token expired (default: 60).

    Returns
    -------
    bool
        True if token is expired or expiring soon, False if still valid.

    """
    return _token_storage._is_token_expired(tokens, buffer_seconds=buffer_seconds)


def refresh_tokens(
    hps_url: str | None = None,
    issuer: str | None = None,
    storage: str = "keyring",
    service_name: str | None = None,
) -> dict | None:
    """Refresh saved tokens using refresh_token.

    Parameters
    ----------
    hps_url:
        HPS server URL. If not provided, will be loaded from saved tokens.
    issuer:
        OIDC issuer URL. If not provided, defaults to standard OIDC discovery path.

    Returns
    -------
    dict | None
        Refreshed token dict if successful, None if refresh fails or no tokens available.

    """
    from ...authenticate import authenticate, determine_auth_url

    # Load saved tokens from the selected backend only.
    tokens = load_tokens(storage=storage, service_name=service_name)
    if not tokens:
        print("No saved tokens found. Run login first.", file=sys.stderr)
        return None

    if not hps_url:
        hps_url = tokens.get("hps_url")
    if not hps_url:
        print("HPS URL not found in saved tokens. Please provide --url.", file=sys.stderr)
        return None

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        print("No refresh_token available. Re-login required.", file=sys.stderr)
        return None

    try:
        # Determine auth URL from HPS server or use provided issuer
        if issuer:
            auth_url = f"{issuer.rstrip('/')}/protocol/openid-connect/token"
        else:
            auth_url = determine_auth_url(hps_url, verify_ssl=False, fallback_realm=REALM)
            if not auth_url:
                auth_url = f"{hps_url.rstrip('/')}/auth/realms/{REALM}"

        # Use authenticate with refresh_token grant
        new_tokens = authenticate(
            auth_url=auth_url,
            grant_type="refresh_token",
            client_id=CLIENT_ID,
            refresh_token=refresh_token,
            verify=False,
        )
        return new_tokens
    except Exception as e:
        print(f"Token refresh failed: {e}", file=sys.stderr)
        return None


def _oidc_endpoints(hps_url: str, issuer: str | None = None) -> dict:
    """Fetch OIDC endpoint URLs from the OIDC discovery endpoint.

    Parameters
    ----------
    hps_url:
        Base URL of the HPS server. Used to construct default issuer if not provided.
    issuer:
        OIDC issuer URL. If not provided, defaults to HPS Keycloak issuer path.

    Returns
    -------
    dict
        Dictionary with 'authorization_endpoint' and 'token_endpoint' keys.

    """
    if issuer is None:
        # Default to HPS Keycloak issuer
        issuer = f"{hps_url.rstrip('/')}/auth/realms/{REALM}"

    discovery_url = f"{issuer.rstrip('/')}/.well-known/openid-configuration"
    r = requests.get(discovery_url, verify=False, timeout=10)
    r.raise_for_status()
    cfg = r.json()
    return {
        "authorization_endpoint": cfg["authorization_endpoint"],
        "token_endpoint": cfg["token_endpoint"],
    }


def _pkce_pair() -> tuple[str, str]:
    """Generate a PKCE (verifier, challenge) pair using S256."""
    verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def browser_login(hps_url: str, open_browser: bool = True, issuer: str | None = None) -> dict:
    """Run the OIDC Authorization Code + PKCE flow.

    Starts a temporary localhost HTTP server on port ``REDIRECT_PORT``,
    opens the login page in the default browser, and exchanges
    the returned authorization code for tokens.

    Parameters
    ----------
    hps_url:
        Base URL of the HPS server, e.g. ``https://localhost:8443/hps``.
    open_browser:
        Whether to automatically open the authorization URL in the default browser.
    issuer:
        OIDC issuer URL. If not provided, defaults to HPS Keycloak issuer.

    Returns
    -------
    dict
        Token response containing ``access_token``, ``refresh_token``,
        ``expires_in``, ``refresh_expires_in``, ``token_type``, etc.

    """
    endpoints = _oidc_endpoints(hps_url, issuer=issuer)
    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(16)

    # ── Result container shared between the callback handler and this thread ──
    result: dict = {}
    event = threading.Event()

    class _CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            if "code" in params:
                result["code"] = params["code"][0]
                result["state"] = params.get("state", [None])[0]
                self._respond(200, "Login successful! You can close this tab.")
            elif "error" in params:
                result["error"] = params["error"][0]
                result["error_description"] = params.get("error_description", [""])[0]
                self._respond(400, f"Login failed: {result['error']}")
            else:
                self._respond(400, "Unexpected callback.")
            event.set()

        def _respond(self, code: int, message: str):
            body = (
                f"<html><body style='font-family:sans-serif;padding:2em'>"
                f"<h2>{message}</h2>"
                f"<p>Return to your terminal.</p></body></html>"
            ).encode()
            self.send_response(code)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass  # suppress server log noise

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), _CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # ── Build authorization URL ───────────────────────────────────────────────
    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = endpoints["authorization_endpoint"] + "?" + urllib.parse.urlencode(auth_params)

    print()
    print("=" * 60)
    print("  Opening browser for HPS login...")
    print()
    print(f"  URL: {auth_url}")
    print("=" * 60)
    print()

    if open_browser:
        try:
            webbrowser.open(auth_url)
        except Exception:
            print("  (Could not open browser automatically - copy the URL above)")
    print("Waiting for browser login", end="", flush=True)

    # ── Wait for callback (up to 5 minutes) ──────────────────────────────────
    signalled = event.wait(timeout=300)
    server.shutdown()

    if not signalled:
        raise RuntimeError("Login timed out (5 minutes). Please try again.")

    if "error" in result:
        raise RuntimeError(
            f"Login failed: {result['error']} - {result.get('error_description', '')}"
        )

    if result.get("state") != state:
        raise RuntimeError("State mismatch - possible CSRF. Aborting.")

    print(" done")

    # ── Exchange code for tokens ──────────────────────────────────────────────
    token_resp = requests.post(
        endpoints["token_endpoint"],
        data={
            "client_id": CLIENT_ID,
            "grant_type": "authorization_code",
            "code": result["code"],
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier,
        },
        verify=False,
        timeout=15,
    )
    token_resp.raise_for_status()
    return token_resp.json()


def save_tokens(
    tokens: dict,
    hps_url: str,
    storage: str = "memory",
    service_name: str | None = None,
) -> Path | None:
    """Persist tokens to specified storage location.

    Parameters
    ----------
    tokens:
        Token response dict returned by OIDC provider.
    hps_url:
        HPS server URL to record alongside the tokens.
    storage:
        Where to save tokens (default: "memory"):
        - "memory": Keep in memory only, do not persist (returns None)
        - "disk": Save to disk with platform-specific security
          (DPAPI on Windows, 0o600 permissions on Unix/Linux)
        - "keyring": Save to system keyring only
    service_name:
        Optional keyring service name used when ``storage="keyring"``.
        If omitted, the value of ``HPS_OIDC_KEYRING_SERVICE_NAME`` is used.
        If the env var is not set, defaults to ``"ansys-hps"``.

    Returns
    -------
    Path | None
        Path of disk file if saved to disk, otherwise None.

    Raises
    ------
    ValueError
        If storage method, hps_url, or token payload schema is invalid.
    RuntimeError
        If ``storage="keyring"`` is requested and keyring persistence fails.

    """
    _token_storage.TOKEN_FILE = TOKEN_FILE
    return _token_storage.save_tokens(
        tokens=tokens,
        hps_url=hps_url,
        storage=storage,
        service_name=service_name,
    )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="OIDC browser login (Authorization Code + PKCE)")
    parser.add_argument(
        "--url",
        default="https://localhost:8443/hps",
        help="Server URL (default: https://localhost:8443/hps)",
    )
    parser.add_argument(
        "--issuer",
        help="OIDC issuer URL. If not provided, defaults to HPS Keycloak issuer path",
    )
    parser.add_argument(
        "--client-id",
        help="OIDC client ID (default: rep-cli for HPS)",
    )
    parser.add_argument(
        "--refresh-only",
        action="store_true",
        help="Refresh saved tokens without performing login. "
        "Loads tokens from the selected storage backend and refreshes them.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the URL instead of opening the browser automatically",
    )
    parser.add_argument(
        "--save-to-disk",
        action="store_true",
        help="Persist tokens to disk (default: keep in memory only)",
    )
    parser.add_argument(
        "--use-keyring",
        action="store_true",
        help="Save tokens to system keyring (Credential Manager/Keychain/Secret Service). "
        "Requires 'keyring' package.",
    )
    parser.add_argument(
        "--print-token",
        action="store_true",
        help="Print the access token to stdout after login (useful for scripting)",
    )
    args = parser.parse_args()

    # Handle token refresh
    if args.refresh_only:
        print("Refreshing saved tokens...")
        storage = "keyring" if args.use_keyring else "disk" if args.save_to_disk else "keyring"
        new_tokens = refresh_tokens(
            args.url if args.url != "https://localhost:8443/hps" else None,
            issuer=args.issuer,
            storage=storage,
        )
        if new_tokens:
            # Save refreshed tokens back
            save_tokens(new_tokens, new_tokens.get("hps_url", args.url), storage=storage)
            print("Tokens refreshed successfully")
            print(
                f"Access token expires in {new_tokens.get('expires_in', '?')}s, "
                f"refresh token expires in {new_tokens.get('refresh_expires_in', '?')}s"
            )
            if args.print_token:
                print(new_tokens["access_token"])
        else:
            print("Token refresh failed", file=sys.stderr)
            sys.exit(1)
        return

    # Normal login flow
    print(f"Connecting to: {args.url}")
    try:
        tokens = browser_login(args.url, open_browser=not args.no_browser, issuer=args.issuer)
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine storage method
    storage = "keyring" if args.use_keyring else "disk" if args.save_to_disk else "memory"
    path = save_tokens(tokens, args.url, storage=storage)

    if path:
        if platform.system() == "Windows":
            print(f"Tokens encrypted and saved to {path} (DPAPI)")
        else:
            print(f"Tokens saved to {path} (mode 0o600)")
    elif storage == "keyring":
        print("Tokens saved to system keyring")
    else:
        print("Tokens kept in memory (not persisted to disk)")
    print(
        f"Access token expires in {tokens.get('expires_in', '?')}s, "
        f"refresh token expires in {tokens.get('refresh_expires_in', '?')}s"
    )

    if args.print_token:
        print(tokens["access_token"])


if __name__ == "__main__":
    main()
