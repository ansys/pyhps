# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri O.Koenig
# ----------------------------------------------------------
import logging

import requests
from requests.adapters import HTTPAdapter, Retry

log = logging.getLogger(__name__)


def create_session(
    access_token: str = None,
    verify: bool | str = True,
    disable_insecure_warnings=False,
) -> requests.Session:
    """Returns a :class:`requests.Session` object configured for REP with given access token

    Parameters
    ----------
    access_token : str
        The access token provided by :meth:`ansys.rep.client.auth.authenticate`

    Returns
    -------
    :class:`requests.Session`
        The session object.
    verify: bool | str, optional
        Either a boolean, in which case it controls whether we verify the
        server's TLS certificate, or a string, in which case it must be
        a path to a CA bundle to use.
        See the :class:`requests.Session` doc.
    disable_insecure_warnings: bool, optional
        Disable warnings about insecure HTTPS requests.
    """
    session = requests.Session()

    # Disable SSL certificate verification and warnings about it
    session.verify = verify

    if disable_insecure_warnings:
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )

    # Set basic content type to json
    session.headers = {
        "content-type": "text/json",
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
