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

"""Module providing the base class for all client and server HPS-related errors."""

import logging

from requests.exceptions import RequestException

log = logging.getLogger(__name__)


class HPSError(RequestException):
    """Provides the base class for all HPS-related errors.

    This class derives from the :class:`requests.exceptions.RequestException`
    base class.

    Example:
    -------
        >>> from ansys.hps.client import HPSError
        >>> from ansys.hps.client.jms import Client
        >>> try:
        >>>     client = Client(url="https://127.0.0.1:8443/hps/",
                                username="repuser",
                                password="wrong_psw")
        >>> except HPSError as e:
        >>>     print(e)
        401 Client Error: invalid_grant for: POST https://127.0.0.1:8443/hps/auth...
        Invalid user credentials

    """

    def __init__(self, *args, **kwargs):
        """Initialize the HPSError object."""
        self.reason = kwargs.pop("reason", None)
        self.description = kwargs.pop("description", None)
        super().__init__(*args, **kwargs)


class APIError(HPSError):
    """Provides server-side related errors."""

    def __init__(self, *args, **kwargs):
        """Initialize the APIError object."""
        super().__init__(*args, **kwargs)


class ClientError(HPSError):
    """Provides client-side related errors."""

    def __init__(self, *args, **kwargs):
        """Initialize the ClientError object."""
        super().__init__(*args, **kwargs)


class VersionCompatibilityError(ClientError):
    """Provides version compatibility errors."""

    def __init__(self, *args, **kwargs):
        """Initialize the VersionCompatibilityError object."""
        super().__init__(*args, **kwargs)


description_fields = ["description", "error_description", "detail"]


def _build_error_message(category, response):
    """Builds an error message from a response object."""
    r_content = {}
    try:
        r_content = response.json()
    except ValueError:
        pass

    reason = r_content.get("title", None)  # jms api
    if not reason:
        reason = r_content.get("error", None)  # auth api
    if not reason:
        reason = response.reason

    description = None
    for field in description_fields:
        description = r_content.get(field, None)
        if description:
            break

    msg = (
        f"{response.status_code} {category}: {reason} for: {response.request.method} {response.url}"
    )
    if description:
        msg += f"\n{description}"

    return reason, description, msg


def raise_for_status(response, *args, **kwargs):
    """Automatically checks HTTP errors.

    This method mimics the requests.Response.raise_for_status() method.
    """
    if 400 <= response.status_code < 500:
        reason, description, message = _build_error_message("Client Error", response)
        raise ClientError(message, reason=reason, description=description, response=response)
    elif 500 <= response.status_code < 600:
        reason, description, message = _build_error_message("Server Error", response)
        raise APIError(message, reason=reason, description=description, response=response)
    return response
