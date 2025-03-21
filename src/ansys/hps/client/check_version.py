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

"""
Version compatibility checks.
"""

from functools import wraps
from typing import Protocol

from .exceptions import VersionCompatibilityError


class API(Protocol):
    """Protocol for API classes."""

    @property
    def version(self) -> str:
        pass


def check_min_version(version, min_version) -> bool:
    """Check if a version string meets a minimum version.

    Parameters
    ----------
    version : str
        Version string to check. For example, ``"1.32.1"``.
    min_version : str
        Required version for comparison. For example, ``"1.32.2"``.

    Returns
    -------
    bool
         ``True`` when successful, ``False`` when failed.
    """
    from packaging.version import parse

    return parse(version) >= parse(min_version)


def check_max_version(version, max_version) -> bool:
    """Check if a version string meets a maximum version.

    Parameters
    ----------
    version : str
        Version string to check. For example, ``"1.32.1"``.
    max_version : str
        Required version for comparison. For example, ``"1.32.2"``.

    Returns
    -------
    bool
         ``True`` when successful, ``False`` when failed.
    """
    from packaging.version import parse

    return parse(version) <= parse(max_version)


def check_version_and_raise(version, min_version=None, max_version=None, msg=None):

    if min_version is not None and not check_min_version(version, min_version):

        if msg is None:
            msg = f"Version {version} is not supported. Minimum version required: {min_version}"
        raise VersionCompatibilityError(msg)

    if max_version is not None and not check_max_version(version, max_version):

        if msg is None:
            msg = f"Version {version} is not supported. Maximum version required: {max_version}"
        raise VersionCompatibilityError(msg)


def version_required(min_version=None, max_version=None):
    """Decorator for API methods to check version requirements."""

    def decorator(func):

        @wraps(func)
        def wrapper(self: API, *args, **kwargs):
            if min_version is not None and not check_min_version(self.version, min_version):
                raise VersionCompatibilityError(
                    f"{func.__name__} requires {type(self).__name__} version >= " + min_version
                )

            if max_version is not None and not check_max_version(self.version, max_version):
                raise VersionCompatibilityError(
                    f"{func.__name__} requires {type(self).__name__} version <= " + min_version
                )
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
