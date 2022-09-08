# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from marshmallow import fields

from ansys.rep.client.common import ObjectSchema

from .fitness_definition import FitnessDefinitionSchema
from .object_reference import IdReferenceList

log = logging.getLogger(__name__)


class JobDefinitionSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    name = fields.String(allow_none=True, description="Name of the job definition")
    active = fields.Boolean(
        description="Defines whether this is the active job definition in the "
        "project where evaluators will evaluate pending jobs"
    )
    creation_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the job definition was created.",
    )
    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the job definition was last modified.",
    )

    parameter_definition_ids = IdReferenceList(
        referenced_class="ParameterDefinition", attribute="parameter_definition_ids", description=""
    )
    parameter_mapping_ids = IdReferenceList(
        referenced_class="ParameterMapping", attribute="parameter_mapping_ids", description=""
    )
    task_definition_ids = IdReferenceList(
        referenced_class="TaskDefinition", attribute="task_definition_ids", description=""
    )

    fitness_definition = fields.Nested(
        FitnessDefinitionSchema,
        allow_none=True,
        description="A :class:`FitnessDefinition` object.",
    )
