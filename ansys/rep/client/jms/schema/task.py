# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

from marshmallow import fields

from ansys.rep.client.common import ObjectSchemaWithModificationInfo

from .object_reference import IdReference, IdReferenceList
from .task_definition import TaskDefinitionSchema


class TaskSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    pending_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "The date and time the task was set to pending."},
    )
    prolog_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "The date and time the task was set to prolog."},
    )
    running_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "The date and time the task was set to running."},
    )
    finished_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "The date and time the task was completed."},
    )

    eval_status = fields.String(allow_none=True, metadata={"description": "Evaluation status."})
    trial_number = fields.Integer(
        allow_none=True,
        load_only=True,
        metadata={"description": "Which attempt to execute the process step this task represent."},
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
        metadata={"description": "ID of the :class:`TaskDefinition` " "the task is linked to."},
    )
    task_definition_snapshot = fields.Nested(
        TaskDefinitionSchema,
        allow_none=True,
        metadata={
            "description": "Snapshot of :class:`TaskDefinition` "
            "created when task status changes to prolog, before evaluation."
        },
    )

    executed_command = fields.String(allow_none=True)

    job_id = IdReference(
        allow_none=False,
        attribute="job_id",
        referenced_class="Job",
        metadata={"description": "ID of the :class:`Job` the task is linked to."},
    )

    host_id = fields.String(
        allow_none=True,
        metadata={"description": "UUID of the :class:`Evaluator` that updated the task."},
    )

    input_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="input_file_ids",
        metadata={"description": "List of IDs of input files of task."},
    )
    output_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="output_file_ids",
        metadata={"description": "List of IDs of output files of task."},
    )
    monitored_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="monitored_file_ids",
        metadata={"description": "List of IDs of monitored files of task."},
    )

    inherited_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="inherited_file_ids",
        metadata={"description": "List of IDs of inherited files of task."},
    )
    owned_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="owned_file_ids",
        metadata={"description": "List of IDs of owned files of task."},
    )

    license_context_id = fields.String(
        allow_none=True,
        metadata={"description": "ID of license context in use"},
    )

    custom_data = fields.Dict(
        allow_none=True,
        dmetadata={"description": "Dictionary type field to store custom data."},
    )
