from marshmallow import fields

from ansys.rep.client.common import BaseSchema


class PermissionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    permission_type = fields.String(required=True)
    value_id = fields.String(required=True)
    value_name = fields.String(allow_none=True)
    role = fields.String(required=True)
