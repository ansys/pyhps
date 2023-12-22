# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields

from ansys.hps.client.common import BaseSchema


class ProjectSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    id = fields.Str(
        metadata={
            "description": "Unique ID to access the project, assigned server side on creation."
        }
    )
    name = fields.Str(metadata={"description": "Name of the project."})
    active = fields.Bool(
        metadata={"description": "Defines whether the project is active for evaluation."}
    )
    priority = fields.Int(metadata={"description": "Priority to pick the project for evaluation."})

    creation_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "The date and time the project was created."},
    )
    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "The date and time the project was last modified."},
    )

    statistics = fields.Dict(
        load_only=True,
        metadata={"description": "Optional dictionary containing various project statistics."},
    )
