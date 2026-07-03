"""OIDC login with system keyring storage.

Demonstrates how to save tokens to the system credential manager:
- Windows: Credential Manager
- macOS: Keychain
- Linux: Secret Service (via python-keyring)

Requires: pip install keyring

This example also demonstrates creating ``Client`` with
``token_storage=\"keyring\"`` so automatic refresh updates are persisted
to keyring across runs.
"""

from ansys.hps.client import Client
from ansys.hps.client.auth.api.oidc_login import browser_login, save_tokens


def main():
    """Perform OIDC login and save tokens to system keyring."""
    hps_url = "https://localhost:8443/hps"
    storage_mode = "keyring"

    # Perform login
    tokens = browser_login(hps_url=hps_url)

    # Save tokens to system keyring (preferred storage method)
    try:
        result = save_tokens(tokens, hps_url=hps_url, storage=storage_mode)
    except RuntimeError as ex:
        print(str(ex))
        return None

    # Configure Client to persist automatic token refresh updates to keyring.
    _ = Client(
        url=hps_url,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        token_storage=storage_mode,
    )

    if result is None:
        print("Tokens saved to system keyring")
        print("Client token_storage is set to 'keyring' for persistent refresh updates")

    print(f"Token Expires In: {tokens.get('expires_in')} seconds")

    return tokens


if __name__ == "__main__":
    main()
