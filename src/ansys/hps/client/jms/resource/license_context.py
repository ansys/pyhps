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

# DO NOT EDIT.
# This file is automatically generated from the JMS schemas.

"""Module providing the license context resource."""
from datetime import datetime
from typing import Any, Dict, List, Union

from marshmallow.utils import missing

from ansys.hps.client.common import Object

from ..schema.license_context import LicenseContextSchema


class LicenseContext(Object):
    """Provides the license context resource.

    Parameters
    ----------
    context_id : str, optional
        License context ID.
    environment : dict, optional
        License context environment dict.
    """

    class Meta:
        schema = LicenseContextSchema
        rest_name = "license_contexts"

    def __init__(self, context_id: str = missing, environment: Dict = missing, **kwargs):
        self.context_id = context_id
        self.environment = environment

        self.obj_type = self.__class__.__name__


LicenseContextSchema.Meta.object_class = LicenseContext
