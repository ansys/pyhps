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
"""Module providing task schema."""

from marshmallow import fields

from ansys.hps.client.common import ObjectSchemaWithModificationInfo

from .object_reference import IdReference, IdReferenceList
from .task_definition import TaskDefinitionSchema


class TaskSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    pending_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Date and time that the task was set to pending."},
    )
    prolog_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Date and time that the task was set to prolog."},
    )
    running_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Date and time that the task was set to running."},
    )
    finished_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Date and time that the task was completed."},
    )

    eval_status = fields.String(allow_none=True, metadata={"description": "Evaluation status."})
    trial_number = fields.Integer(
        allow_none=True,
        load_only=True,
        metadata={"description": "Which attempt to execute the process step this task represents."},
    )
    elapsed_time = fields.Float(
        allow_none=True,
        load_only=True,
        metadata={"description": "Number of seconds it took the evaluator to execute the task."},
    )

    task_definition_id = IdReference(
        allow_none=False,
        attribute="task_definition_id",
        referenced_class="TaskDefinition",
        metadata={
            "description": "ID of the :class:`TaskDefinition` instance that the task is linked to."
        },
    )
    task_definition_snapshot = fields.Nested(
        TaskDefinitionSchema,
        allow_none=True,
        metadata={
            "description": "Snapshot of the  :class:`TaskDefinition` instance that was created"
            " when the task status changed to prolog, before evaluation."
        },
    )

    executed_command = fields.String(allow_none=True)

    job_id = IdReference(
        allow_none=False,
        attribute="job_id",
        referenced_class="Job",
        metadata={"description": "ID of the :class:`Job` instance that the task is linked to."},
    )

    host_id = fields.String(
        allow_none=True,
        metadata={"description": "UUID of the :class:`Evaluator` instance that updated the task."},
    )

    input_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="input_file_ids",
        metadata={"description": "List of IDs of input files of the task."},
    )
    output_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="output_file_ids",
        metadata={"description": "List of IDs of output files of the task."},
    )
    monitored_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="monitored_file_ids",
        metadata={"description": "List of IDs of monitored files of the task."},
    )

    inherited_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="inherited_file_ids",
        metadata={"description": "List of IDs of inherited files of the task."},
    )
    owned_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="owned_file_ids",
        metadata={"description": "List of IDs of owned files of the task."},
    )

    license_context_id = fields.String(
        allow_none=True,
        metadata={"description": "ID of the license context in use."},
    )

    custom_data = fields.Dict(
        allow_none=True,
        metadata={"description": "Dictionary type field for storing custom data."},
    )

    working_directory = fields.String(
        allow_none=True,
        metadata={"description": "Working directory of the task."},
    )
