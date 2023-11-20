# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields
from marshmallow.validate import OneOf

from ansys.rep.client.common import ObjectSchemaWithModificationInfo

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
        metadata={"description": "ID of the linked job definition, " "see :class:`JobDefinition`."},
    )

    priority = fields.Integer(
        allow_none=True,
        metadata={
            "description": "Priority with which jobs are evaluated. The default is 0, "
            "which is the highest priority. Assigning a higher value to a job "
            "makes it a lower priority."
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
    note = fields.String(allow_none=True, metadata={"description": "Optional note for this job."})
    creator = fields.String(
        allow_none=True, metadata={"description": "Optional name/ID of the creator of this job."}
    )

    executed_level = fields.Integer(
        allow_none=True,
        metadata={
            "description": "Execution level of the last executed "
            "task (-1 if none has been executed yet)."
        },
    )

    elapsed_time = fields.Float(
        load_only=True,
        metadata={"description": "Number of seconds it took the evaluator(s) to update the job."},
    )

    host_ids = fields.List(
        fields.String(allow_none=True),
        allow_none=True,
        metadata={"description": "List of Host IDs of the evaluators that updated the job."},
    )
    file_ids = IdReferenceList(
        referenced_class="File",
        attribute="file_ids",
        load_only=True,
        metadata={"description": "List of IDs of all files of this job."},
    )
