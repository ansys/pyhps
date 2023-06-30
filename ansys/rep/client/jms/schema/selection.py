# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields

from ansys.rep.client.common import ObjectSchemaWithModificationInfo

from .object_reference import IdReference, IdReferenceList


class JobSelectionSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(description="Name of the selection.")

    algorithm_id = IdReference(
        allow_none=True,
        attribute="algorithm_id",
        referenced_class="DesignExplorationAlgorithm",
        description="ID of the :class:`Algorithm` " "the selection belongs to (optional).",
    )
    object_ids = IdReferenceList("Job", attribute="jobs", description="List of job IDs.")
