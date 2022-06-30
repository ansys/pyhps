# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

from marshmallow import fields

from .base import BaseSchema


class ProjectPermissionSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        pass

    permission_type = fields.String(required=True)
    value_id = fields.String(required=True)
    value_name = fields.String(allow_none=True)
    role = fields.String(required=True)
