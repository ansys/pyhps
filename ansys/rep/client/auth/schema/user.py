# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging

from marshmallow import fields

from ansys.rep.client.common.base_schema import BaseSchema

log = logging.getLogger(__name__)

_admin_keys = {
    "groups": set(["admin"]),
    "realm_roles": set(["admin"]),
}


def _check_admin(obj):
    for name, grp in _admin_keys.items():
        values = obj.get(name, [])
        if grp.intersection(values):
            return True
    return False


class UserSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    id = fields.String(
        load_only=True,
        description="Unique user ID, generated internally by the server on creation.",
    )
    username = fields.Str(description="Username.")
    password = fields.Str(dump_only=True, description="Password.")
    firstName = fields.Str(allow_none=True, description="First name", attribute="first_name")
    lastName = fields.Str(allow_none=True, description="Last name", attribute="last_name")
    email = fields.Str(allow_none=True, description="E-mail address (optional).")
