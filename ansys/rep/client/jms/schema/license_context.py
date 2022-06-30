# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from .base import BaseSchema
from .object_reference import IdReference, IdReferenceList

class LicenseContextSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        pass

    context_id = fields.String(allow_none=True, load_only=True, description="License context ID")
    environment = fields.Dict(allow_none=True, description="License context environment dict")
