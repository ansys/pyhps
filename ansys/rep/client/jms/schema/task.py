# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

from marshmallow import fields

from ansys.rep.client.common import ObjectSchema

from .object_reference import IdReference, IdReferenceList
from .task_definition import TaskDefinitionSchema


class TaskSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    modification_time = fields.DateTime(
        allow_none=True, load_only=True, description="The date and time the task was last modified."
    )
    creation_time = fields.DateTime(
        allow_none=True, load_only=True, description="The date and time the task was created."
    )
    pending_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the task was set to pending.",
    )
    prolog_time = fields.DateTime(
        allow_none=True, load_only=True, description="The date and time the task was set to prolog."
    )
    running_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the task was set to running.",
    )
    finished_time = fields.DateTime(
        allow_none=True, load_only=True, description="The date and time the task was completed."
    )

    eval_status = fields.String(allow_none=True, description="Evaluation status.")
    trial_number = fields.Integer(
        allow_none=True,
        load_only=True,
        description="Which attempt to execute the process step this task represent.",
    )
    elapsed_time = fields.Float(
        allow_none=True,
        load_only=True,
        description="Number of seconds it took the evaluator to execute the task.",
    )

    task_definition_id = IdReference(
        allow_none=False,
        attribute="task_definition_id",
        referenced_class="TaskDefinition",
        description="ID of the :class:`TaskDefinition` " "the task is linked to.",
    )
    task_definition_snapshot = fields.Nested(
        TaskDefinitionSchema,
        allow_none=True,
        description="Snapshot of :class:`TaskDefinition` "
        "created when task status changes to prolog, before evaluation.",
    )

    job_id = IdReference(
        allow_none=False,
        attribute="job_id",
        referenced_class="Job",
        description="ID of the :class:`Job` the task is linked to.",
    )

    host_id = fields.String(
        allow_none=True,
        description="UUID of the :class:`Evaluator` that updated the task.",
    )

    input_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="input_file_ids",
        description="List of IDs of input files of task.",
    )
    output_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="output_file_ids",
        description="List of IDs of output files of task.",
    )

    inherited_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="inherited_file_ids",
        description="List of IDs of inherited files of task.",
    )
    owned_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="owned_file_ids",
        description="List of IDs of owned files of task.",
    )

    license_context_id = fields.String(
        allow_none=True,
        metadata={"description": "ID of license context in use"},
    )
