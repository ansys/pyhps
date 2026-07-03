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

"""Load and use previously saved tokens.

Demonstrates how to load tokens from an explicitly selected storage backend
and use them in API calls.
"""

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
