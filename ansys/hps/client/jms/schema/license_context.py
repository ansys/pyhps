# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from ansys.rep.client.common import BaseSchema
from marshmallow import fields


class LicenseContextSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    context_id = fields.String(
        allow_none=True, load_only=True, metadata={"description": "License context ID"}
    )
    environment = fields.Dict(
        allow_none=True, metadata={"description": "License context environment dict"}
    )
