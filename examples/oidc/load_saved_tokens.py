# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import logging

from ansys.hps.client.auth.api.oidc_login import _is_token_expired, load_tokens

log = logging.getLogger(__name__)


def main():
    """Load saved tokens and use them."""
    # Select which backend to load from: "keyring" or "disk"
    storage_mode = "keyring"
    verify_ssl = False

    tokens = load_tokens(storage=storage_mode)

    if not tokens:
        log.info("No saved tokens found in %s storage. Please run login first.", storage_mode)
        return

    log.info("Loaded tokens for: %s", tokens.get("hps_url"))

    if not tokens.get("access_token"):
        log.info("No access token is persisted by design. Refresh to obtain a new access token.")
        return

    # Check if token is expired (with 60 second buffer)
    if _is_token_expired(tokens, buffer_seconds=60):
        log.info("Token is expired or expiring soon. Please refresh.")
        return

    log.info("Token is valid")
    log.info("Access Token: %s...", tokens["access_token"][:50])
    log.info("TLS certificate verification enabled: %s", verify_ssl)

    # Example: Use the token in API calls
    # response = requests.get(
    #     "https://localhost:8443/hps/api/v1/projects",
    #     headers={"Authorization": f"Bearer {tokens['access_token']}"},
    #     verify=verify_ssl,
    # )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
