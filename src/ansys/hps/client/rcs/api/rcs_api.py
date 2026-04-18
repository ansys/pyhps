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
"""Module wrapping around RCS root endpoints."""

import logging

from ansys.hps.client.client import Client
from ansys.hps.client.exceptions import ClientError
from ansys.hps.client.rcs.models import (
    RegisterInstance,
    RegisterInstanceResponse,
    UnRegisterInstance,
    UnRegisterInstanceResponse,
)

from .base import create_object, delete_object

log = logging.getLogger(__name__)


class RcsApi:
    """Wraps around the RCS root endpoints.

    Parameters
    ----------
    client : Client
        HPS client object.

    """

    def __init__(self, client: Client):
        """Initialize the ``RmsApi`` object."""
        self.client = client
        self._health_check = None
        self._api_info = None
        # Perform the health check during initialization
        if not self.health:
            raise ClientError("The RCS API is not alive. Cannot initialize RcsApi.")

    @property
    def url(self) -> str:
        """URL of the API."""
        return f"{self.client.url}/rcs"

    def health_check(self):
        """Check the health of the RCS API."""
        if self._health_check is None:
            r = self.client.session.get(f"{self.url}/healthz")
            self._health_check = r.json()
        return self._health_check

    @property
    def health(self) -> bool:
        """Health status of the RCS API."""
        return self.health_check().get("status") == "alive"

    def get_api_info(self):
        """Get information on the RMS API the client is connected to.

        The information includes the version and build date.
        """
        if self._api_info is None:
            r = self.client.session.get(f"{self.url}/api/v1")
            self._api_info = r.json()
        return self._api_info

    @property
    def version(self) -> str:
        """API version."""
        return self.get_api_info()["build"]["version"]

    ################################################################
    # register instance
    def register_instance(self, data: RegisterInstance) -> RegisterInstanceResponse:
        """Register an instance to RCS."""
        return create_object(
            self.client.session,
            self.url,
            data,
            as_object=True,
        )

    # unregister instance
    def unregister_instance(self, data: UnRegisterInstance) -> UnRegisterInstanceResponse:
        """Unregister an instance from RCS."""
        return delete_object(
            self.client.session,
            self.url,
            data,
            as_object=True,
        )
