"""OIDC login with system keyring storage.

Demonstrates how to save tokens to the system credential manager:
- Windows: Credential Manager
- macOS: Keychain
- Linux: Secret Service (via python-keyring)

Requires: pip install keyring
"""

from ansys.hps.client.auth.api.oidc_login import browser_login, save_tokens


def main():
    """Perform OIDC login and save tokens to system keyring."""
    # Perform login
    tokens = browser_login(hps_url="https://localhost:8443/hps")

    # Save tokens to system keyring (preferred storage method)
    result = save_tokens(tokens, hps_url="https://localhost:8443/hps", storage="keyring")

    if result is None and storage == "keyring":
        print("Tokens saved to system keyring")
    else:
        print(f"Tokens saved to disk at: {result}")

    print(f"Token Expires In: {tokens.get('expires_in')} seconds")

    return tokens


if __name__ == "__main__":
    main()
