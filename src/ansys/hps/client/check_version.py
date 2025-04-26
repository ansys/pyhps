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

"""Version compatibility checks."""

import logging
from enum import Enum
from functools import wraps
from typing import Protocol

from .exceptions import VersionCompatibilityError

log = logging.getLogger(__name__)


class HpsRelease(Enum):
    """HPS release versions."""

    v1_0_2 = "1.0.2"
    v1_1_1 = "1.1.1"
    v1_2_0 = "1.2.0"


"""HPS to JMS version mapping."""
JMS_VERSIONS: dict[HpsRelease, str] = {
    HpsRelease.v1_0_2: "1.0.12",
    HpsRelease.v1_1_1: "1.0.20",
    HpsRelease.v1_2_0: "1.1.4",
}


"""HPS to RMS version mapping."""
RMS_VERSIONS: dict[HpsRelease, str] = {
    HpsRelease.v1_0_2: "1.0.0",
    HpsRelease.v1_1_1: "1.1.5",
    HpsRelease.v1_2_0: "1.1.10",
}


class ApiProtocol(Protocol):
    """Protocol for API classes."""

    @property
    def version(self) -> str:
        """API version."""
        pass


def check_min_version(version: str, min_version: str) -> bool:
    """Check if a version string meets a minimum version."""
    from packaging.version import parse

    if version in ["0.0.dev", "0.0.0"]:
        log.warning("Skipping min version check for backend development version")
        return True

    return parse(version) >= parse(min_version)


def check_max_version(version: str, max_version: str) -> bool:
    """Check if a version string meets a maximum version."""
    from packaging.version import parse

    if version in ["0.0.dev", "0.0.0"]:
        log.warning("Skipping max version check for backend development version")
        return True

    return parse(version) <= parse(max_version)


def check_min_version_and_raise(version, min_version: str, msg=None):
    """Check if a version meets a minimum version, raise an exception if not."""
    if not check_min_version(version, min_version):
        if msg is None:
            msg = f"Version {version} is not supported. Minimum version required: {min_version}"
        raise VersionCompatibilityError(msg)


def check_max_version_and_raise(version, max_version: str, msg=None):
    """Check if a version meets a maximum version, raise an exception if not."""
    if not check_max_version(version, max_version):
        if msg is None:
            msg = f"Version {version} is not supported. Maximum version required: {max_version}"
        raise VersionCompatibilityError(msg)


def check_version_and_raise(
    version, min_version: str | None = None, max_version: str | None = None, msg=None
):
    """Check if a version meets the min/max requirements, raise an exception if not."""
    if min_version is not None:
        check_min_version_and_raise(version, min_version, msg)

    if max_version is not None:
        check_max_version_and_raise(version, max_version, msg)


def version_required(min_version=None, max_version=None):
    """Provide a decorator for API methods to check version requirements."""

    def decorator(func):
        @wraps(func)
        def wrapper(self: ApiProtocol, *args, **kwargs):
            if min_version is not None:
                msg = f"{func.__name__} requires {type(self).__name__} version >= " + min_version
                check_min_version_and_raise(self.version, min_version, msg)

            if max_version is not None:
                msg = f"{func.__name__} requires {type(self).__name__} version <= " + max_version
                check_max_version_and_raise(self.version, max_version, msg)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
