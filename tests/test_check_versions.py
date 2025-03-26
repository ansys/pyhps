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
# SOFTWARE.get_projects

import pytest

from ansys.hps.client.check_version import check_version_and_raise, version_required
from ansys.hps.client.exceptions import VersionCompatibilityError


def test_check_version_and_raise():
    with pytest.raises(VersionCompatibilityError) as excinfo:
        check_version_and_raise(version="1.0.5", min_version="1.0.6", max_version="1.0.10")
    assert "Minimum version required: 1.0.6" in str(excinfo.value)

    with pytest.raises(VersionCompatibilityError) as excinfo:
        check_version_and_raise(version="1.0.11", min_version="1.0.6", max_version="1.0.10")
    assert "Maximum version required: 1.0.10" in str(excinfo.value)

    check_version_and_raise(version="1.0.6", min_version="1.0.6", max_version="1.0.10")
    check_version_and_raise(version="1.0.8", min_version="1.0.6", max_version="1.0.10")
    check_version_and_raise(version="1.0.10", min_version="1.0.6", max_version="1.0.10")


def test_version_required():
    class MockApi:
        def __init__(self, version):
            self.version = version

        @version_required(min_version="1.0.6", max_version="2.1.4")
        def fn1(self):
            return True

        @version_required(max_version="2.1.4")
        def fn2(self):
            return True

        @version_required(min_version="0.1.8")
        def fn3(self):
            return True

    # test fn1 - bound to min and max version
    with pytest.raises(VersionCompatibilityError) as excinfo:
        MockApi("3.4.5").fn1()
    assert "version <= 2.1.4" in str(excinfo.value)

    with pytest.raises(VersionCompatibilityError) as excinfo:
        MockApi("0.1.2").fn1()
    assert "version >= 1.0.6" in str(excinfo.value)

    assert MockApi("1.2.77").fn1()
    assert MockApi("2.1.4").fn1()
    assert MockApi("1.2.77-beta").fn1()

    # test fn2 - bound to max version
    with pytest.raises(VersionCompatibilityError) as excinfo:
        MockApi("3.4.5").fn1()
    assert "version <= 2.1.4" in str(excinfo.value)

    assert MockApi("0.0.0").fn2()
    assert MockApi("2.1.4").fn2()

    # test fn3 - bound to min version
    with pytest.raises(VersionCompatibilityError) as excinfo:
        MockApi("0.1.7").fn3()
    assert "version >= 0.1.8" in str(excinfo.value)

    assert MockApi("0.1.8").fn3()
    assert MockApi("1.2.3").fn3()

    # test skipping check for dev version
    assert MockApi("0.0.dev").fn1()
    assert MockApi("0.0.0").fn2()
    assert MockApi("0.0.dev").fn3()
