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
"""Module providing project schema."""

from marshmallow import fields

from ansys.hps.client.common import BaseSchema


class ProjectSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    id = fields.Str(
        metadata={
            "description": "Unique ID to access the project, assigned server side on creation."
        }
    )
    name = fields.Str(metadata={"description": "Name of the project."})
    active = fields.Bool(
        metadata={"description": "Defines whether the project is active for evaluation."}
    )
    priority = fields.Int(
        metadata={"description": "Priority for picking the project for evaluation."}
    )

    creation_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Date and time that the project was created."},
    )
    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Date and time that the project was last modified."},
    )

    statistics = fields.Dict(
        load_only=True,
        allow_none=True,
        metadata={"description": "Dictionary containing various project statistics."},
    )
