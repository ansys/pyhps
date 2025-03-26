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
"""Module providing restricted value fields."""

from marshmallow import fields
from marshmallow.exceptions import ValidationError


class RestrictedValue(fields.Field):
    """Restricted value fields."""

    restricted_fields = [
        fields.Int(strict=True),
        fields.Bool(truthy=[True], falsy=[False]),
        fields.Str(),
        fields.Float(allow_nan=False),
    ]

    def __init__(self):
        """Initialize a RestrictedValue object."""
        super().__init__(allow_none=True)

    def _deserialize(self, value, attr, obj, **kwargs):
        """Convert string to restricted value object."""
        for field in self.restricted_fields:
            try:
                return field._deserialize(value, attr, obj, **kwargs)
            except Exception:
                pass

        self.raise_validation_error()

    def raise_validation_error():
        """Raise validation error if value is not a float, integer, Boolean, or string."""
        raise ValidationError("Value must be a float, integer, Boolean, or string.")
