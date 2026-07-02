"""Basic OIDC login example.

Demonstrates how to perform an OIDC login and use the access token.
Tokens are kept in memory only (not persisted).

If these tokens are passed to ``Client`` without ``token_storage``, refreshed
tokens also remain in memory only and are not persisted across runs.
"""

from ansys.hps.client import Client
from ansys.hps.client.auth.api.oidc_login import browser_login


def main():
    """Perform OIDC login and print the access token."""
    hps_url = "https://localhost:8443/hps"
    storage_mode = "memory"

    # Perform login - opens browser for authentication
    tokens = browser_login(hps_url=hps_url)

    # Configure Client with explicit in-memory refresh persistence mode.
    _ = Client(
        url=hps_url,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        token_storage=storage_mode,
    )

    # Access token is now available
    print(f"\nAccess Token: {tokens['access_token'][:50]}...")
    print(f"Token Expires In: {tokens.get('expires_in')} seconds")
    print("Client token_storage is set to 'memory' (refresh updates are in-process only)")

    # Use the access token in your API calls
    # Example: requests.get(url, headers={"Authorization": f"Bearer {tokens['access_token']}"})

    return tokens


if __name__ == "__main__":
    main()
