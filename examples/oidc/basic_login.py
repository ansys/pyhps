"""Basic OIDC login example.

Demonstrates how to perform an OIDC login and use the access token.
Tokens are kept in memory only (not persisted).
"""

from ansys.hps.client.auth.api.oidc_login import browser_login


def main():
    """Perform OIDC login and print the access token."""
    # Perform login - opens browser for authentication
    tokens = browser_login(hps_url="https://localhost:8443/hps")

    # Access token is now available
    print(f"\nAccess Token: {tokens['access_token'][:50]}...")
    print(f"Token Expires In: {tokens.get('expires_in')} seconds")

    # Use the access token in your API calls
    # Example: requests.get(url, headers={"Authorization": f"Bearer {tokens['access_token']}"})

    return tokens


if __name__ == "__main__":
    main()
