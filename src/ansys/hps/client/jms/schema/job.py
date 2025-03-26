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
"""Module providing job schema."""

from marshmallow import fields
from marshmallow.validate import OneOf

from ansys.hps.client.common import ObjectSchemaWithModificationInfo

from .object_reference import IdReference, IdReferenceList

valid_eval_status = [
    "inactive",
    "pending",
    "prolog",
    "running",
    "evaluated",
    "failed",
    "aborted",
    "timeout",
]


class JobSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(allow_none=True, metadata={"description": "Name of the job."})
    eval_status = fields.String(
        validate=OneOf(valid_eval_status), metadata={"description": "Evaluation status."}
    )
    job_definition_id = IdReference(
        allow_none=False,
        attribute="job_definition_id",
        referenced_class="JobDefinition",
        metadata={
            "description": "ID of the linked job definition. "
            "For more information, see the :class:`JobDefinition` class."
        },
    )

    priority = fields.Integer(
        allow_none=True,
        metadata={
            "description": "Priority for evaluating the job. "
            "The default is ``0``, which is the highest priority. "
            "Assigning a higher value to a job makes it a lower priority."
        },
    )
    values = fields.Dict(
        keys=fields.String(),
        allow_none=True,
        metadata={
            "description": "Dictionary with (name,value) pairs for all parameters defined in the "
            "linked job definition."
        },
    )
    fitness = fields.Float(allow_none=True, metadata={"description": "Fitness value computed."})
    fitness_term_values = fields.Dict(
        keys=fields.String(),
        values=fields.Float(allow_none=True),
        allow_none=True,
        metadata={
            "description": "Dictionary with (name,value) pairs for all fitness terms computed."
        },
    )
    note = fields.String(allow_none=True, metadata={"description": "Note for the job."})
    creator = fields.String(
        allow_none=True,
        metadata={"description": "Additional information about the creator of the job."},
    )

    executed_level = fields.Integer(
        allow_none=True,
        metadata={
            "description": "Execution level of the last executed task. "
            "A value of ``-1`` indicates that no task has been executed yet."
        },
    )

    elapsed_time = fields.Float(
        load_only=True,
        metadata={"description": "Number of seconds it took the evaluators to update the job."},
    )

    host_ids = fields.List(
        fields.String(allow_none=True),
        allow_none=True,
        metadata={"description": "List of host IDs of the evaluators that updated the job."},
    )
    file_ids = IdReferenceList(
        referenced_class="File",
        attribute="file_ids",
        load_only=True,
        metadata={"description": "List of IDs of all files of the job."},
    )
