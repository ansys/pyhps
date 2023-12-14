# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from ansys.rep.client.common import ObjectSchemaWithModificationInfo
from marshmallow import fields

from .object_reference import IdReferenceList


class AlgorithmSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(allow_none=True, metadata={"description": "Name of the algorithm."})
    description = fields.String(
        allow_none=True, metadata={"description": "Description of the algorithm."}
    )

    data = fields.String(
        allow_none=True,
        metadata={
            "description": "Generic string field to hold arbitrary algorithm configuration data,"
            " e.g. as JSON dictionary.",
        },
    )
    job_ids = IdReferenceList("Job", attribute="jobs", metadata={"description": "List of job IDs."})
