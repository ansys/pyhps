"""OIDC browser login for HPS using Authorization Code + PKCE.

Starts a temporary localhost HTTP server, opens your browser at the
Keycloak login page, and exchanges the authorization code for tokens.
No password is ever entered in the terminal.

Usage
-----
    uv run python oidc_login.py --url https://cdc04hps02:8443/hps

The resulting tokens are saved to ``~/.ansys/hps_tokens.json`` and can be
consumed by the ``reconnect`` MCP tool or any script that reads them.
"""

import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests  # noqa: E402

TOKEN_FILE = Path.home() / ".ansys" / "hps_tokens.json"
CLIENT_ID = "rep-cli"
REALM = "rep"
REDIRECT_PORT = 19876
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"


def _oidc_endpoints(hps_url: str) -> dict:
    """Fetch OIDC endpoint URLs from Keycloak's well-known discovery document."""
    discovery_url = (
        f"{hps_url.rstrip('/')}/auth/realms/{REALM}/.well-known/openid-configuration"
    )
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


def browser_login(hps_url: str, open_browser: bool = True) -> dict:
    """Run the OIDC Authorization Code + PKCE flow against HPS Keycloak.

    Starts a temporary localhost HTTP server on port ``REDIRECT_PORT``,
    opens the Keycloak login page in the default browser, and exchanges
    the returned authorization code for tokens.

    Parameters
    ----------
    hps_url:
        Base URL of the HPS server, e.g. ``https://localhost:8443/hps``.
    open_browser:
        Whether to automatically open the authorization URL in the default browser.

    Returns
    -------
    dict
        Token response containing ``access_token``, ``refresh_token``,
        ``expires_in``, ``refresh_expires_in``, ``token_type``, etc.

    """
    endpoints = _oidc_endpoints(hps_url)
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


def save_tokens(tokens: dict, hps_url: str) -> Path:
    """Persist tokens to ``~/.ansys/hps_tokens.json``.

    Parameters
    ----------
    tokens:
        Token response dict returned by Keycloak.
    hps_url:
        HPS server URL to record alongside the tokens.

    Returns
    -------
    Path
        Path of the written file.

    """
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "hps_url": hps_url,
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "expires_in": tokens.get("expires_in"),
        "refresh_expires_in": tokens.get("refresh_expires_in"),
        "saved_at": time.time(),
    }
    TOKEN_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    TOKEN_FILE.chmod(0o600)
    return TOKEN_FILE


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="HPS OIDC browser login (Authorization Code + PKCE)")
    parser.add_argument(
        "--url",
        default="https://localhost:8443/hps",
        help="HPS server URL (default: https://localhost:8443/hps)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the URL instead of opening the browser automatically",
    )
    parser.add_argument(
        "--print-token",
        action="store_true",
        help="Print the access token to stdout after login (useful for scripting)",
    )
    args = parser.parse_args()

    print(f"Connecting to: {args.url}")
    try:
        tokens = browser_login(args.url, open_browser=not args.no_browser)
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

    path = save_tokens(tokens, args.url)
    print(f"Tokens saved to {path}")
    print(f"Access token expires in {tokens.get('expires_in', '?')}s, "
          f"refresh token expires in {tokens.get('refresh_expires_in', '?')}s")

    if args.print_token:
        print(tokens["access_token"])


if __name__ == "__main__":
    main()
