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

"""Basic OIDC login example.

Demonstrates how to perform an OIDC login and use the access token.
Tokens are kept in memory only (not persisted).

If these tokens are passed to ``Client`` without ``token_storage``, refreshed
tokens also remain in memory only and are not persisted across runs.
"""

import logging

from ansys.hps.client import Client
from ansys.hps.client.auth.api.oidc_login import browser_login

log = logging.getLogger(__name__)


def main():
    """Perform OIDC login and log the access token."""
    hps_url = "https://localhost:8443/hps"
    storage_mode = "memory"
    verify_ssl = False

    # Perform login - opens browser for authentication
    tokens = browser_login(hps_url=hps_url, verify_ssl=verify_ssl)

    # Configure Client with explicit in-memory refresh persistence mode.
    _ = Client(
        url=hps_url,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        token_storage=storage_mode,
        verify=verify_ssl,
    )

    # Access token is now available
    log.info("Access Token: %s...", tokens["access_token"][:50])
    log.info("Token Expires In: %s seconds", tokens.get("expires_in"))
    log.info("TLS certificate verification enabled: %s", verify_ssl)
    log.info("Client token_storage is set to 'memory' (refresh updates are in-process only)")

    # Use the access token in your API calls
    # Example: requests.get(url, headers={"Authorization": f"Bearer {tokens['access_token']}"})

    return tokens


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
