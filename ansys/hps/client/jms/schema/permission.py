from marshmallow import fields

from ansys.hps.client.common import BaseSchema


class PermissionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    permission_type = fields.String(
        required=True, metadata={"description": "Either 'user', 'group', or 'anyone'."}
    )
    value_id = fields.String(
        allow_none=True, metadata={"description": "Can be the ID of a user or group."}
    )
    value_name = fields.String(allow_none=True)
    role = fields.String(
        required=True, metadata={"description": "Either 'admin', 'writer',  or 'reader'."}
    )
