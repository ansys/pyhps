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

"""Shared argparse utilities for HPS client examples."""

import argparse

from ansys.hps.client import Client

# Parent parser with connection arguments shared by all examples.
# Must use add_help=False so child parsers can provide their own -h/--help.
base_parser = argparse.ArgumentParser(add_help=False)
base_parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
base_parser.add_argument("-u", "--username", default=None)
base_parser.add_argument("-p", "--password", default=None)
base_parser.add_argument(
    "--access-token", default=None, help="Access token (alternative to username/password)."
)
base_parser.add_argument(
    "--api-key", default=None, help="API key (alternative to username/password)."
)


def client_from_args(args) -> Client:
    """Create a :class:`Client` from parsed command-line arguments.

    Falls back to no authentication if no credentials are provided.
    """
    if args.api_key:
        return Client(url=args.url, api_key=args.api_key)
    if args.access_token:
        return Client(url=args.url, access_token=args.access_token)
    if args.username and args.password:
        return Client(url=args.url, username=args.username, password=args.password)
    return Client(url=args.url)
