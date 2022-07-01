# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields
from marshmallow.validate import OneOf

from .base import ObjectSchema
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


class JobSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    name = fields.String(allow_none=True, description="Name of the design point.")
    eval_status = fields.String(validate=OneOf(valid_eval_status), description="Evaluation status.")
    job_definition_id = IdReference(
        allow_none=False,
        attribute="job_definition_id",
        referenced_class="JobDefinition",
        description="ID of the linked job_definition, see :class:`ansys.rep.client.jms.JobDefinition`.",
    )

    priority = fields.Integer(
        allow_none=True,
        default=0,
        description="Priority with which design points are evaluated. The default is 0, which is the highest priority. Assigning a higher value to a design point makes it a lower priority.",
    )
    values = fields.Dict(
        keys=fields.String(),
        allow_none=True,
        description="Dictionary with (name,value) pairs for all parameters defined in the linked job_definition.",
    )
    fitness = fields.Float(allow_none=True, description="Fitness value computed.")
    fitness_term_values = fields.Dict(
        keys=fields.String(),
        values=fields.Float(allow_none=True),
        allow_none=True,
        description="Dictionary with (name,value) pairs for all fitness terms computed.",
    )
    note = fields.String(allow_none=True, description="Optional note for this design point.")
    creator = fields.String(
        allow_none=True, description="Optional name/ID of the creator of this design point."
    )
    executed_task_definition_level = fields.Integer(
        allow_none=True,
        description="Execution level of the last executed process step (-1 if none has been executed yet).",
    )

    creation_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the design point was created.",
    )
    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the design point was last modified.",
    )
    elapsed_time = fields.Float(
        load_only=True,
        description="Number of seconds it took the evaluator(s) to update the design point.",
    )

    evaluators = fields.List(
        fields.String(allow_none=True),
        allow_none=True,
        description="List of UUID strings of the evaluators that updated the design point.",
    )
    file_ids = IdReferenceList(
        referenced_class="File",
        attribute="file_ids",
        load_only=True,
        description="List of IDs of all files of this design point.",
    )
