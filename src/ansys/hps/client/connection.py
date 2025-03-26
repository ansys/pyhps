# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Utilities to configure a :class:`requests.Session` object."""

import logging

import requests
from requests.adapters import HTTPAdapter, Retry

log = logging.getLogger(__name__)


def create_session(
    access_token: str = None,
    verify: bool | str = True,
    disable_security_warnings=False,
) -> requests.Session:
    """Get the :class:`requests.Session` object configured for HPS with a given access token.

    Parameters
    ----------
    access_token : str
        Access token provided by the :meth:`ansys.hps.client.auth.authenticate` method.
    verify: Union[bool, str], optional
        If a Boolean, whether to verify the server's TLS certificate. The default is ``True``.
        If a string, the path to the CA bundle to use. For more information, see the
        :class:`requests.Session` documentation.
    disable_security_warnings: bool, optional
        Whether to disable warnings about insecure HTTPS requests. The default is ``False``.

    Returns
    -------
    :class:`requests.Session`
        Session object.

    """
    session = requests.Session()

    # Disable SSL certificate verification and warnings about it
    session.verify = verify

    if disable_security_warnings:
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )

    # Set basic content type to json
    session.headers.update({"content-type": "application/json"})

    if access_token:
        session.headers.update({"Authorization": f"Bearer {access_token}"})

    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def ping(session: requests.Session, url: str, timeout=10.0) -> bool:
    """Ping the given URL.

    Parameters
    ----------
    session : :class:`requests.Session`
        Session object.
    url : str
        URL address to ping.
    timeout : float, optional
        Time in seconds to continue pinging the URL before reporting a failure. The
        default is ``10.0``.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.

    """
    log.debug(f"Ping {url} ...")
    r = session.get(url, timeout=timeout)
    success = r.status_code == requests.codes.ok
    if success:
        log.debug("Ping successful")
    else:
        log.debug(f"Ping failed, HTTP error {r.status_code}")
    return success
