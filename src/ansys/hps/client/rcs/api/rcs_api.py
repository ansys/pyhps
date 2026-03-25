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

import inspect
import logging

from ansys.hps.client.check_version import status_required
from ansys.hps.client.client import Client
from ansys.hps.client.rcs.models import (
    RegisterInstance,
    RegisterInstanceResponse,
    UnRegisterInstance,
    UnRegisterInstanceResponse,
)

from .base import create_object, delete_object

log = logging.getLogger(__name__)


def apply_status_check(cls):
    """Apply the status_required decorator to all methods in the class."""
    excluded_methods = {"health", "health_check"}  # Methods to exclude from decoration
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        # Skip special methods and excluded methods
        if not name.startswith("__") and name not in excluded_methods:
            # Apply the status_required decorator dynamically
            setattr(cls, name, status_required()(method))
    return cls


@apply_status_check
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
