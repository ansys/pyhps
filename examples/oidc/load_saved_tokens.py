"""Load and use previously saved tokens.

Demonstrates how to load tokens from storage (keyring or disk)
and use them in API calls.
"""

from ansys.hps.client.auth.api.oidc_login import load_tokens, _is_token_expired
import requests


def main():
    """Load saved tokens and use them."""
    # Load tokens from storage (tries keyring first, then disk)
    tokens = load_tokens()

    if not tokens:
        print("No saved tokens found. Please run login first.")
        return

    print(f"Loaded tokens for: {tokens.get('hps_url')}")

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
    #     verify=False
    # )


if __name__ == "__main__":
    main()
