"""OIDC login with disk storage.

Demonstrates how to save tokens to disk with platform-specific security:
- Windows: Encrypted with DPAPI (user-scoped) at %USERPROFILE%\.ansys\hps_tokens.json
- Unix/Linux: Plaintext with restrictive permissions (0o600) at ~/.ansys/hps_tokens.json

This example also demonstrates creating ``Client`` with
``token_storage=\"disk\"`` so automatic refresh updates are persisted
to disk across runs.
"""

from ansys.hps.client import Client
from ansys.hps.client.auth.api.oidc_login import browser_login, save_tokens


def main():
    """Perform OIDC login and save tokens to disk."""
    hps_url = "https://localhost:8443/hps"
    storage_mode = "disk"

    # Perform login
    tokens = browser_login(hps_url=hps_url)

    # Save tokens to disk
    token_file = save_tokens(tokens, hps_url=hps_url, storage=storage_mode)

    # Configure Client to persist automatic token refresh updates to disk.
    _ = Client(
        url=hps_url,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        token_storage=storage_mode,
    )

    print(f"Tokens saved to: {token_file}")
    print("Client token_storage is set to 'disk' for persistent refresh updates")
    print(f"Token Expires In: {tokens.get('expires_in')} seconds")

    return tokens


if __name__ == "__main__":
    main()
