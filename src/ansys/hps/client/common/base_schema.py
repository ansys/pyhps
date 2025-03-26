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
"""Module providing base schemas and object schemas with and without modification information."""

from marshmallow import INCLUDE, Schema, fields, post_load


class BaseSchema(Schema):
    """Base schema class."""

    class Meta:
        """Meta class for the schema."""

        ordered = True
        unknown = INCLUDE
        object_class = None  # To be set in derived objects

    @post_load
    def make_object(self, data, **kwargs):
        """Make object for base schema."""
        return self.Meta.object_class(**data)


class ObjectSchema(BaseSchema):
    """Create object schema with ID."""

    id = fields.String(
        allow_none=True,
        attribute="id",
        metadata={
            "description": "Unique ID to access the resource, generated "
            "internally by the server on creation."
        },
    )


class ObjectSchemaWithModificationInfo(ObjectSchema):
    """Object schema with creation & modification times, and created & modified by fields."""

    creation_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={
            "description": "Date and time that the resource was created.",
        },
    )
    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={
            "description": "Date and time that the resource was last modified.",
        },
    )

    created_by = fields.String(
        allow_none=True,
        load_only=True,
        metadata={
            "description": "ID of the user who created the object.",
        },
    )
    modified_by = fields.String(
        allow_none=True,
        load_only=True,
        metadata={
            "description": "ID of the user who last modified the object.",
        },
    )
