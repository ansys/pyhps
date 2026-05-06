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

"""Example to submit a nonlinear tire analysis job to HPS.

This is the Ansys Parametric Design Language (APDL) Tire Performance Simulation example included
in the technology demonstration guide (td-57).
"""

import argparse
import logging

import jwt
from ansys.rep.common.auth.self_signed_token_provider import SelfSignedTokenProvider

log = logging.getLogger(__name__)


def _main(log, args):
    if not args.token or not args.signing_key:
        raise RuntimeError("Need token and signing key set to function.")
    payload = jwt.decode(
        args.token,
        options={
            "verify_signature": False,
            "verify_aud": False,
            "verify_iss": False,
            "verify_exp": False,
        },
    )
    if "UID" in payload:
        user_id = payload["UID"]
    else:
        user_id = payload["sub"]
    provider = SelfSignedTokenProvider({"hps-default": args.signing_key})
    if args.account:
        extra = {"account_admin": True, "oid": user_id}
    else:
        extra = {"service_admin": True, "oid": user_id}
    token = provider.generate_signed_token(user_id, user_id, args.account, 6000, extra)
    print(token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", default="")
    parser.add_argument("-a", "--account", default="")
    parser.add_argument("-s", "--signing_key", default="")

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    _main(log, args)
