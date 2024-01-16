# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from marshmallow import fields

from ansys.hps.client.common import ObjectSchemaWithModificationInfo

from .fitness_definition import FitnessDefinitionSchema
from .object_reference import IdReferenceList

log = logging.getLogger(__name__)


class JobDefinitionSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(allow_none=True, metadata={"description": "Name of the job definition"})
    active = fields.Boolean(
        metadata={
            "description": "Defines whether this is the active job definition in the "
            "project where evaluators will evaluate pending jobs"
        }
    )
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
