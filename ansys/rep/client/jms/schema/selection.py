# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields

from .base import ObjectSchema
from .object_reference import IdReference, IdReferenceList


class JobSelectionSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    name = fields.String(description="Name of the selection.")

    creation_time = fields.DateTime(
        allow_none=True, load_only=True, description="The date and time the selection was created."
    )
    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the selection was last modified.",
    )

    algorithm_id = IdReference(
        allow_none=True,
        attribute="algorithm_id",
        referenced_class="DesignExplorationAlgorithm",
        description="ID of the :class:`ansys.rep.client.jms.Algorithm` "
        "the selection belongs to (optional).",
    )
    object_ids = IdReferenceList("Job", attribute="jobs", description="List of design point IDs.")
