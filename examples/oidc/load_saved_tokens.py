"""Load and use previously saved tokens.

Demonstrates how to load tokens from an explicitly selected storage backend
and use them in API calls.
"""

import requests

from ansys.hps.client.auth.api.oidc_login import _is_token_expired, load_tokens


def main():
    """Load saved tokens and use them."""
    # Select which backend to load from: "keyring" or "disk"
    storage_mode = "keyring"

    tokens = load_tokens(storage=storage_mode)

    if not tokens:
        print(f"No saved tokens found in {storage_mode} storage. Please run login first.")
        return

    print(f"Loaded tokens for: {tokens.get('hps_url')}")

    if not tokens.get("access_token"):
        print("No access token is persisted by design. Refresh to obtain a new access token.")
        return

    # Check if token is expired (with 60 second buffer)
    if _is_token_expired(tokens, buffer_seconds=60):
        print("Token is expired or expiring soon. Please refresh.")
        return

    print("Token is valid")
    print(f"Access Token: {tokens['access_token'][:50]}...")

    # Example: Use the token in API calls
    # response = requests.get(
    #     "https://localhost:8443/hps/api/v1/projects",
    #     headers={"Authorization": f"Bearer {tokens['access_token']}"},
    #     verify=False,
    # )


if __name__ == "__main__":
    main()
