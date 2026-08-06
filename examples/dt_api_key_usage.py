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

"""Example: authenticate with API token and create a JMS project.

This example uses the new ``api_token`` client input.

- JMS requests are sent with:
  ``X-API-Key: ApiKey <token>``
- DT receives:
  ``token = \"ApiKey <token>\"``

Usage
-----
python dt_api_key_usage.py --hps-url https://localhost:8443/hps --api-token <token> --insecure
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone

from ansys.hps.data_transfer.client.models import OperationState, StoragePath

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import JmsApi, Project

log = logging.getLogger(__name__)


def create_simple_project(hps_url: str, api_token: str, verify_ssl: bool) -> Project:
    """Create a simple JMS project using API-token authentication."""
    client = Client(
        url=hps_url,
        api_token=api_token,
        verify=verify_ssl,
    )

    # Initialize DT and run a DT operation before any JMS calls.
    client.initialize_data_transfer_client()
    dt_folder = f"api-key-example/{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    op = client.data_transfer_api.mkdir([StoragePath(path=dt_folder)])
    op = client.data_transfer_api.wait_for(op.id)[0]
    if op.state != OperationState.Succeeded:
        raise HPSError(f"Failed to create DT folder: {dt_folder}")
    log.info("Created DT folder: %s", dt_folder)

    jms_api = JmsApi(client)
    project_name = f"API Key Example {datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    project = Project(name=project_name, priority=1, active=True)

    created = jms_api.create_project(project, replace=False)
    log.info("Created project: id=%s name=%s", created.id, created.name)
    return created


def main() -> int:
    """Parse CLI args and run the example."""
    parser = argparse.ArgumentParser(
        description="Use an API token with pyhps and create a simple JMS project."
    )
    parser.add_argument("--url", default="https://localhost:8443/hps", help="Base HPS URL")
    parser.add_argument("--api-key", required=True, help="API token value")
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for local/self-signed endpoints.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        _ = create_simple_project(
            hps_url=args.url,
            api_token=args.api_key,
            verify_ssl=not args.insecure,
        )
    except HPSError as ex:
        log.error("HPS error: %s", ex)
        return 1
    except Exception as ex:  # pragma: no cover - defensive for a user-facing script
        log.error("Unexpected error: %s", ex)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
