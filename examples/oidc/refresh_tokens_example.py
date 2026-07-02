"""Refresh saved tokens.

Demonstrates how to refresh tokens using the refresh_token grant for an
explicitly selected storage backend.
"""

from ansys.hps.client.auth.api.oidc_login import load_tokens, refresh_tokens, save_tokens


def main():
    """Refresh saved tokens."""
    # Select which backend to use: "keyring" or "disk"
    storage_mode = "keyring"

    # Load current tokens from selected storage
    current_tokens = load_tokens(storage=storage_mode)

    if not current_tokens:
        print(f"No saved tokens found in {storage_mode} storage. Please run login first.")
        return

    print("Refreshing tokens...")

    # Refresh the tokens from the same selected backend
    new_tokens = refresh_tokens(
        hps_url=current_tokens.get("hps_url"),
        storage=storage_mode,
    )

    if not new_tokens:
        print("Token refresh failed. You may need to login again.")
        return

    # Save refreshed tokens back to the same storage backend
    result = save_tokens(new_tokens, new_tokens.get("hps_url"), storage=storage_mode)

    if storage_mode == "keyring":
        print("New tokens saved to system keyring")
    else:
        print(f"New tokens saved to disk at: {result}")

    print(f"New token expires in: {new_tokens.get('expires_in')} seconds")
    print(f"New refresh token expires in: {new_tokens.get('refresh_expires_in')} seconds")


if __name__ == "__main__":
    main()

