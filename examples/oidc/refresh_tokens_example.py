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

"""Refresh saved tokens.

Demonstrates how to refresh tokens using the refresh_token grant for an
explicitly selected storage backend.
"""

import logging

from ansys.hps.client.auth.api.oidc_login import load_tokens, refresh_tokens, save_tokens


log = logging.getLogger(__name__)


def main():
    """Refresh saved tokens."""
    # Select which backend to use: "keyring" or "disk"
    storage_mode = "keyring"

    # Load current tokens from selected storage
    current_tokens = load_tokens(storage=storage_mode)

    if not current_tokens:
        log.info("No saved tokens found in %s storage. Please run login first.", storage_mode)
        return

    log.info("Refreshing tokens...")

    # Refresh the tokens from the same selected backend
    new_tokens = refresh_tokens(
        hps_url=current_tokens.get("hps_url"),
        storage=storage_mode,
    )

    if not new_tokens:
        log.info("Token refresh failed. You may need to login again.")
        return

    # Save refreshed tokens back to the same storage backend
    result = save_tokens(new_tokens, new_tokens.get("hps_url"), storage=storage_mode)

    if storage_mode == "keyring":
        log.info("New tokens saved to system keyring")
    else:
        log.info("New tokens saved to disk at: %s", result)

    log.info("New token expires in: %s seconds", new_tokens.get("expires_in"))
    log.info("New refresh token expires in: %s seconds", new_tokens.get("refresh_expires_in"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()





