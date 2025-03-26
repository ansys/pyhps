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
"""Module providing parameter mapping schema."""

import logging

from marshmallow import fields

from ansys.hps.client.common import ObjectSchemaWithModificationInfo

from .object_reference import IdReference

log = logging.getLogger(__name__)


class ParameterMappingSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    line = fields.Int(allow_none=True)
    column = fields.Int(allow_none=True)
    key_string = fields.String(allow_none=True)
    float_field = fields.String(allow_none=True)
    width = fields.Int(allow_none=True)
    precision = fields.Int(allow_none=True)
    tokenizer = fields.String(allow_none=True, metadata={"description": ""})
    decimal_symbol = fields.String(allow_none=True)
    digit_grouping_symbol = fields.String(allow_none=True)
    string_quote = fields.String(allow_none=True)
    true_string = fields.String(allow_none=True)
    false_string = fields.String(allow_none=True)
    parameter_definition_id = IdReference(
        allow_none=True,
        attribute="parameter_definition_id",
        referenced_class="ParameterDefinition",
        metadata={
            "description": "ID of the linked parameter definition. "
            "For more information, see the :class:`ParameterDefinition` class."
        },
    )
    task_definition_property = fields.String(allow_none=True)
    file_id = IdReference(
        allow_none=True,
        attribute="file_id",
        referenced_class="File",
        metadata={"description": "ID of the file resource."},
    )
