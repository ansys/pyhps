# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields

from .base import ObjectSchema
from .object_reference import IdReferenceList


class AlgorithmSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    name = fields.String(allow_none=True, description="Name of the algorithm.")
    description = fields.String(allow_none=True, description="Description of the algorithm.")

    creation_time = fields.DateTime(
        allow_none=True, load_only=True, description="The date and time the algorithm was created."
    )
    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the algorithm was last modified.",
    )

    data = fields.String(
        allow_none=True,
        description="Generic string field to hold arbitrary algorithm job_definition data,"
        " e.g. as JSON dictionary.",
    )
    job_ids = IdReferenceList("Job", attribute="jobs", description="List of design point IDs.")
