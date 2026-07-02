"""OIDC login with disk storage.

Demonstrates how to save tokens to disk with platform-specific security:
- Windows: Encrypted with DPAPI (user-scoped) at %USERPROFILE%\.ansys\hps_tokens.json
- Unix/Linux: Plaintext with restrictive permissions (0o600) at ~/.ansys/hps_tokens.json
"""

from ansys.hps.client.auth.api.oidc_login import browser_login, save_tokens


def main():
    """Perform OIDC login and save tokens to disk."""
    # Perform login
    tokens = browser_login(hps_url="https://localhost:8443/hps")

    # Save tokens to disk
    token_file = save_tokens(tokens, hps_url="https://localhost:8443/hps", storage="disk")

    print(f"Tokens saved to: {token_file}")
    print(f"Token Expires In: {tokens.get('expires_in')} seconds")

    return tokens


if __name__ == "__main__":
    main()
