# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""OIDC login with system keyring storage.

Demonstrates how to save refresh-token data to the system credential manager:
- Windows: Credential Manager
- macOS: Keychain
- Linux: Secret Service (via python-keyring)

Requires: pip install keyring

This example also demonstrates creating ``Client`` with
``token_storage=\"keyring\"`` so automatic refresh updates are persisted
to keyring across runs. Access tokens remain memory-only.
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
