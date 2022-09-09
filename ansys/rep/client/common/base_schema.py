# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import INCLUDE, Schema, fields, post_load


class BaseSchema(Schema):
    class Meta:
        ordered = True
        unknown = INCLUDE
        object_class = None  # To be set in derived objects

    @post_load
    def make_object(self, data, **kwargs):
        return self.Meta.object_class(**data)


class ObjectSchema(BaseSchema):

    id = fields.String(
        allow_none=True,
        attribute="id",
        description="Unique ID to access the resource, generated "
        "internally by the server on creation.",
    )
