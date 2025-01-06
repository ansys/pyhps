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
"""Module providing file schema."""

from marshmallow import fields

from ansys.hps.client.common import ObjectSchemaWithModificationInfo

from .object_reference import IdReference


class FileSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(metadata={"description": "Name of the file resource."})
    type = fields.String(
        allow_none=True,
        metadata={
            "description": "Type of the file. This can be any string but using a correct media "
            "type for the given resource is advisable."
        },
    )
    storage_id = fields.String(
        allow_none=True,
        metadata={"description": "File's identifier in the (orthogonal) file storage system"},
    )

    size = fields.Int(allow_none=True)
    hash = fields.String(allow_none=True)

    expiry_time = fields.DateTime(
        allow_none=True,
        metadata={"description": "File expiration time."},
    )

    format = fields.String(allow_none=True)
    evaluation_path = fields.String(
        allow_none=True,
        metadata={
            "description": "Relative path under which the file instance for a "
            "job evaluation will be stored.",
        },
    )

    monitor = fields.Bool(
        allow_none=True, metadata={"description": "Whether to live monitor the file's content."}
    )
    collect = fields.Bool(
        allow_none=True, metadata={"description": "Whether file should be collected per job"}
    )
    collect_interval = fields.Int(
        allow_none=True,
        metadata={
            "description": "Collect frequency for a file with collect=True."
            " Min value limited by the evaluator's settings."
            " 0/None - let the evaluator decide,"
            " other value - interval in seconds"
        },
    )

    reference_id = IdReference(
        attribute="reference_id",
        referenced_class="File",
        allow_none=True,
        metadata={"description": "Reference file from which this one was created"},
    )
