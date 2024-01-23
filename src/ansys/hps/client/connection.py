# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

import logging
from typing import Union

import requests
from requests.adapters import HTTPAdapter, Retry

log = logging.getLogger(__name__)


def create_session(
    access_token: str = None,
    verify: Union[bool, str] = True,
    disable_security_warnings=False,
) -> requests.Session:
    """Returns a :class:`requests.Session` object configured for HPS with given access token

    Parameters
    ----------
    access_token : str
        The access token provided by :meth:`ansys.hps.core.auth.authenticate`
    verify: Union[bool, str], optional
        Either a boolean, in which case it controls whether we verify the
        server's TLS certificate, or a string, in which case it must be
        a path to a CA bundle to use.
        See the :class:`requests.Session` documentation.
    disable_security_warnings: bool, optional
        Disable warnings about insecure HTTPS requests.

    Returns
    -------
    :class:`requests.Session`
        The session object.
    """
    session = requests.Session()

    # Disable SSL certificate verification and warnings about it
    session.verify = verify

    if disable_security_warnings:
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )

    # Set basic content type to json
    session.headers = {
        "content-type": "application/json",
    }

    if access_token:
        session.headers.update({"Authorization": "Bearer %s" % access_token})

    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def ping(session: requests.Session, url: str, timeout=10.0) -> bool:
    """Ping the given URL, returning true on success

    Args:
        session: The :class:`requests.Session` object.
        url (str): The URL address to ping.
    Returns:
        bool: True on success.
    """
    log.debug("Ping %s ..." % url)
    r = session.get(url, timeout=timeout)
    success = r.status_code == requests.codes.ok
    if success:
        log.debug("Ping successful")
    else:
        log.debug("Ping failed, HTTP error %s" % r.status_code)
    return success
