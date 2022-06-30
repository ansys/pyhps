# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F. Negri
# ----------------------------------------------------------

from marshmallow import fields

from .base import ObjectSchema

class TaskDefinitionTemplateSchema(ObjectSchema):

    class Meta(ObjectSchema.Meta):
        pass

    modification_time = fields.DateTime(allow_none=True, load_only=True, description="Last time the object was modified, in UTC")
    creation_time = fields.DateTime(allow_none=True, load_only=True, description="Time when the object was created, in UTC")

    name = fields.String(description="Name of the template")
    application_name = fields.String(description="Name of the application to which the template applies")
    application_version = fields.String(description="Version of the application to which the template applies")

    data = fields.Dict(allow_none=True, description="Template's detailed data")