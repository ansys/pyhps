# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields

from .base import BaseSchema


class ProjectSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    id = fields.Str(
        description="Unique ID to access the project, specified on creation of the project."
    )
    name = fields.Str(description="Name of the project.")
    active = fields.Bool(description="Defines whether the project is active for evaluation.")
    priority = fields.Int(description="Priority to pick the project for evaluation.")

    creation_time = fields.DateTime(
        allow_none=True, load_only=True, description="The date and time the project was created."
    )
    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        description="The date and time the project was last modified.",
    )

    file_storages = fields.List(
        fields.Dict(), description="List of file storages defined for the project."
    )
    statistics = fields.Dict(
        load_only=True, description="Optional dictionary containing various project statistics."
    )
