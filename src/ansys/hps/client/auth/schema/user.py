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
"""Module that creates the user schema."""

from marshmallow import fields

from ansys.hps.client.common.base_schema import BaseSchema


class UserSchema(BaseSchema):
    """Create user schema with ID, username, password, first name, last name, and email."""

    class Meta(BaseSchema.Meta):
        pass

    id = fields.String(
        load_only=True,
        metadata={"description": "Unique user ID, generated internally by the server on creation."},
    )
    username = fields.Str(metadata={"description": "Username."})
    password = fields.Str(dump_only=True, metadata={"description": "Password."})
    firstName = fields.Str(  # noqa
        allow_none=True, metadata={"description": "First name."}, attribute="first_name"
    )
    lastName = fields.Str(  # noqa
        allow_none=True, metadata={"description": "Last name."}, attribute="last_name"
    )
    email = fields.Str(allow_none=True, metadata={"description": "E-mail address."})
