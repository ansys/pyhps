"""Refresh saved tokens.

Demonstrates how to refresh tokens using the refresh_token grant.
Updates both keyring and disk storage with new tokens.
"""

from ansys.hps.client.auth.api.oidc_login import refresh_tokens, save_tokens, load_tokens


def main():
    """Refresh saved tokens."""
    # Load current tokens
    current_tokens = load_tokens()

    if not current_tokens:
        print("No saved tokens found. Please run login first.")
        return

    print("Refreshing tokens...")

    # Refresh the tokens
    new_tokens = refresh_tokens(hps_url=current_tokens.get("hps_url"))

    if not new_tokens:
        print("Token refresh failed. You may need to login again.")
        return

    # Save the refreshed tokens back to storage
    # Determine which storage was used (keyring preferred, then disk)
    result = save_tokens(new_tokens, new_tokens.get("hps_url"), storage="keyring")

    if result is None:
        print("New tokens saved to system keyring")
    else:
        print(f"New tokens saved to disk at: {result}")

    print(f"New token expires in: {new_tokens.get('expires_in')} seconds")
    print(f"New refresh token expires in: {new_tokens.get('refresh_expires_in')} seconds")


if __name__ == "__main__":
    main()
