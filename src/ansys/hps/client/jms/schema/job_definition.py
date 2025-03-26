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
"""Module providing job definition schema."""

import logging

from marshmallow import fields

from ansys.hps.client.common import ObjectSchemaWithModificationInfo

from .fitness_definition import FitnessDefinitionSchema
from .object_reference import IdReferenceList

log = logging.getLogger(__name__)


class JobDefinitionSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(allow_none=True, metadata={"description": "Name of the job definition."})
    active = fields.Boolean(metadata={"description": "Whether this job definition is active."})
    client_hash = fields.String(allow_none=True)

    parameter_definition_ids = IdReferenceList(
        referenced_class="ParameterDefinition",
        attribute="parameter_definition_ids",
        metadata={"description": "List of parameter definition IDs."},
    )
    parameter_mapping_ids = IdReferenceList(
        referenced_class="ParameterMapping",
        attribute="parameter_mapping_ids",
        metadata={"description": "List of parameter mapping IDs."},
    )
    task_definition_ids = IdReferenceList(
        referenced_class="TaskDefinition",
        attribute="task_definition_ids",
        metadata={"description": "List of task definition IDs."},
    )

    fitness_definition = fields.Nested(
        FitnessDefinitionSchema,
        allow_none=True,
        metadata={"description": "A :class:`FitnessDefinition` object."},
    )
