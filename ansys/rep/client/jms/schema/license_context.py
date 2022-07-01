# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields

from .base import BaseSchema


class LicenseContextSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    context_id = fields.String(allow_none=True, load_only=True, description="License context ID")
    environment = fields.Dict(allow_none=True, description="License context environment dict")
