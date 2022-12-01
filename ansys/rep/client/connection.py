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


def create_session(access_token: str = None, pat: str = None) -> requests.Session:
    """Returns a :class:`requests.Session` object configured for REP with given access token

    Args:
        access_token (str): The access token provided by :meth:`ansys.rep.client.auth.authenticate`

    Returns:
        :class:`requests.Session`: The session object.
    """
    session = requests.Session()

    # Disable SSL certificate verification and warnings about it
    session.verify = False
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )

    # Set basic content type to json
    session.headers = {
        "content-type": "text/json",
    }

    if access_token:
        session.headers.update({"Authorization": "Bearer %s" % access_token})
    elif pat:
        session.headers.update({"x-api-key": pat})

    retries = Retry(total=10, backoff_factor=1, status_forcelist=[503])
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
