"""OIDC browser login using Authorization Code + PKCE.

Starts a temporary localhost HTTP server, opens your browser at the
login page, and exchanges the authorization code for tokens.
No password is ever entered in the terminal.

Usage
-----
    uv run python oidc_login.py --url https://localhost:8443/hps

The resulting tokens are saved to ``~/.ansys/hps_tokens.json`` and can be
consumed by any script that reads them.

Token Storage Security:
  - Windows: Tokens are encrypted with DPAPI (user-scoped encryption)
  - Unix/Linux: Tokens file has restricted permissions (0o600)
"""

import argparse
import base64
import hashlib
import http.server
import json
import os
import platform
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


def _encrypt_with_dpapi(data: bytes) -> bytes:
    """Encrypt data using Windows DPAPI (user-scoped).

    Windows-only function. Will raise RuntimeError if called on other platforms.
    """
    if platform.system() != "Windows":
        raise RuntimeError("DPAPI encryption is only available on Windows")

    import ctypes
    import ctypes.wintypes as wintypes

    LocalFree = ctypes.windll.kernel32.LocalFree
    MemoryProtect = ctypes.windll.kernel32.VirtualProtect
    CryptProtectData = ctypes.windll.Crypt32.CryptProtectData

    class DataBlob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(wintypes.BYTE))]

    def dpapi_encrypt(plaintext: bytes) -> bytes:
        plaintext_blob = DataBlob(len(plaintext), ctypes.c_char_p(plaintext))
        ciphertext_blob = DataBlob()
        # CRYPTPROTECT_UI_FORBIDDEN = 0x1
        flags = 0x1
        result = CryptProtectData(
            ctypes.byref(plaintext_blob),
            None,
            None,
            None,
            None,
            flags,
            ctypes.byref(ciphertext_blob),
        )
        if not result:
            raise RuntimeError("Failed to encrypt data with DPAPI")
        ciphertext = bytes(ciphertext_blob.pbData[: ciphertext_blob.cbData])
        LocalFree(ciphertext_blob.pbData)
        return ciphertext

    return dpapi_encrypt(data)


def _decrypt_with_dpapi(ciphertext: bytes) -> bytes:
    """Decrypt data using Windows DPAPI.

    Windows-only function. Will raise RuntimeError if called on other platforms.
    """
    if platform.system() != "Windows":
        raise RuntimeError("DPAPI decryption is only available on Windows")

    import ctypes
    import ctypes.wintypes as wintypes

    LocalFree = ctypes.windll.kernel32.LocalFree
    CryptUnprotectData = ctypes.windll.Crypt32.CryptUnprotectData

    class DataBlob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(wintypes.BYTE))]

    def dpapi_decrypt(ciphertext: bytes) -> bytes:
        ciphertext_blob = DataBlob(len(ciphertext), ctypes.c_char_p(ciphertext))
        plaintext_blob = DataBlob()
        flags = 0x1
        result = CryptUnprotectData(
            ctypes.byref(ciphertext_blob),
            None,
            None,
            None,
            None,
            flags,
            ctypes.byref(plaintext_blob),
        )
        if not result:
            raise RuntimeError("Failed to decrypt data with DPAPI")
        plaintext = bytes(plaintext_blob.pbData[: plaintext_blob.cbData])
        LocalFree(plaintext_blob.pbData)
        return plaintext

    return dpapi_decrypt(ciphertext)


def _save_to_keyring(tokens: dict, hps_url: str) -> bool:
    """Save tokens to system keyring using keyring library.

    Returns True if successful, False if keyring is not available.
    """
    try:
        import keyring
    except ImportError:
        return False

    service_name = "ansys-hps"
    try:
        keyring.set_password(service_name, "hps_url", hps_url)
        keyring.set_password(service_name, "access_token", tokens["access_token"])
        if tokens.get("refresh_token"):
            keyring.set_password(service_name, "refresh_token", tokens["refresh_token"])
        if tokens.get("expires_in"):
            keyring.set_password(service_name, "expires_in", str(tokens["expires_in"]))
        if tokens.get("refresh_expires_in"):
            keyring.set_password(service_name, "refresh_expires_in", str(tokens["refresh_expires_in"]))
        keyring.set_password(service_name, "saved_at", str(time.time()))
        return True
    except Exception as e:
        print(f"Warning: Failed to save tokens to keyring: {e}", file=sys.stderr)
        return False


def _load_from_keyring() -> dict | None:
    """Load tokens from system keyring.

    Returns token dict if available, None if keyring unavailable or no tokens saved.
    """
    try:
        import keyring
    except ImportError:
        return None

    service_name = "ansys-hps"
    try:
        access_token = keyring.get_password(service_name, "access_token")
        if not access_token:
            return None

        return {
            "hps_url": keyring.get_password(service_name, "hps_url"),
            "access_token": access_token,
            "refresh_token": keyring.get_password(service_name, "refresh_token"),
            "expires_in": int(keyring.get_password(service_name, "expires_in") or 3600),
            "refresh_expires_in": int(keyring.get_password(service_name, "refresh_expires_in") or 86400),
            "saved_at": float(keyring.get_password(service_name, "saved_at") or time.time()),
        }
    except Exception:
        return None


def _load_from_disk() -> dict | None:
    """Load tokens from disk file.

    Returns token dict if available, None if file doesn't exist or can't be read.
    """
    if not TOKEN_FILE.exists():
        return None

    try:
        content = TOKEN_FILE.read_bytes()
        # Check if encrypted with DPAPI
        if content.startswith(b"DPAPI:"):
            encrypted = base64.b64decode(content[6:])
            json_data = _decrypt_with_dpapi(encrypted)
            return json.loads(json_data.decode("utf-8"))
        else:
            return json.loads(content.decode("utf-8"))
    except Exception as e:
        print(f"Warning: Failed to load tokens from disk: {e}", file=sys.stderr)
        return None


def load_tokens() -> dict | None:
    """Load saved tokens from keyring (preferred) or disk.

    Returns token dict if available, None if no tokens found or errors occur.
    """
    # Try keyring first
    tokens = _load_from_keyring()
    if tokens:
        return tokens

    # Fall back to disk
    return _load_from_disk()


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
    if "expires_in" not in tokens or "saved_at" not in tokens:
        return True  # Can't determine, assume expired

    elapsed = time.time() - tokens["saved_at"]
    expires_in = tokens["expires_in"]
    return elapsed > (expires_in - buffer_seconds)


def refresh_tokens(hps_url: str | None = None, issuer: str | None = None) -> dict | None:
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
    from .authenticate import authenticate, determine_auth_url

    # Load saved tokens
    tokens = load_tokens()
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


def save_tokens(tokens: dict, hps_url: str, storage: str = "disk") -> Path | None:
    """Persist tokens to specified storage location.

    Parameters
    ----------
    tokens:
        Token response dict returned by OIDC provider.
    hps_url:
        HPS server URL to record alongside the tokens.
    storage:
        Where to save tokens (default: "disk"):
        - "memory": Keep in memory only, do not persist (returns None)
        - "disk": Save to disk with platform-specific security
          (DPAPI on Windows, 0o600 permissions on Unix/Linux)
        - "keyring": Save to system keyring with fallback to disk

    Returns
    -------
    Path | None
        Path of disk file if saved to disk, otherwise None.

    Raises
    ------
    ValueError
        If storage method is invalid.
    """
    if storage not in ("memory", "disk", "keyring"):
        raise ValueError(f"Invalid storage method: {storage}. Must be 'memory', 'disk', or 'keyring'")

    if storage == "memory":
        return None

    # Try keyring if requested
    if storage == "keyring":
        if _save_to_keyring(tokens, hps_url):
            return None  # Saved to keyring, no file path

    # Fall back to disk storage
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    json_data = json.dumps({
        "hps_url": hps_url,
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "expires_in": tokens.get("expires_in"),
        "refresh_expires_in": tokens.get("refresh_expires_in"),
        "saved_at": time.time(),
    }, indent=2).encode("utf-8")

    # Platform-specific security
    if platform.system() == "Windows":
        # Windows: use DPAPI encryption (user-scoped)
        encrypted = _encrypt_with_dpapi(json_data)
        # Write as base64-encoded encrypted data
        TOKEN_FILE.write_bytes(b"DPAPI:" + base64.b64encode(encrypted))
    else:
        # Unix/Linux: use restrictive file permissions
        TOKEN_FILE.write_text(json.dumps({
            "hps_url": hps_url,
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in"),
            "refresh_expires_in": tokens.get("refresh_expires_in"),
            "saved_at": time.time(),
        }, indent=2), encoding="utf-8")
        TOKEN_FILE.chmod(0o600)

    return TOKEN_FILE


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
        "Loads tokens from keyring/disk and refreshes them.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the URL instead of opening the browser automatically",
    )
    parser.add_argument(
        "--keep-in-memory",
        action="store_true",
        help="Keep tokens in memory only; do not persist to disk",
    )
    parser.add_argument(
        "--use-keyring",
        action="store_true",
        help="Save tokens to system keyring (Credential Manager/Keychain/Secret Service). "
        "Falls back to disk if keyring unavailable. Requires 'keyring' package.",
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
        new_tokens = refresh_tokens(
            args.url if args.url != "https://localhost:8443/hps" else None,
            issuer=args.issuer
        )
        if new_tokens:
            # Determine storage method for refreshed tokens
            storage = "keyring" if args.use_keyring else "memory" if args.keep_in_memory else "disk"
            # Save refreshed tokens back
            save_tokens(new_tokens, new_tokens.get("hps_url", args.url), storage=storage)
            print("Tokens refreshed successfully")
            print(f"Access token expires in {new_tokens.get('expires_in', '?')}s, "
                  f"refresh token expires in {new_tokens.get('refresh_expires_in', '?')}s")
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
    storage = "keyring" if args.use_keyring else "memory" if args.keep_in_memory else "disk"
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
    print(f"Access token expires in {tokens.get('expires_in', '?')}s, "
          f"refresh token expires in {tokens.get('refresh_expires_in', '?')}s")

    if args.print_token:
        print(tokens["access_token"])


if __name__ == "__main__":
    main()
