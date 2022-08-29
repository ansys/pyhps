# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F. Negri
# ----------------------------------------------------------

from marshmallow import fields

from .base import ObjectSchema
from .file import FileSchema
from .object_reference import IdReference
from .task_definition import ResourceRequirementsSchema, SoftwareSchema


class TaskDefinitionTemplateSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    modification_time = fields.DateTime(
        allow_none=True, load_only=True, description="Last time the object was modified, in UTC"
    )
    creation_time = fields.DateTime(
        allow_none=True, load_only=True, description="Time when the object was created, in UTC"
    )

    name = fields.String(description="Name of the template")
    version = fields.String(description="version of the template", allow_none=True)

    software_requirements = fields.Nested(SoftwareSchema, many=True, allow_none=True)
    resource_requirements = fields.Nested(ResourceRequirementsSchema, allow_none=True)

    execution_context = fields.Dict(
        allow_none=True, description="Additional arguments to pass to the executing command"
    )
    environment = fields.Dict(
        allow_none=True, description="Environment variables to set for the executed process"
    )

    execution_command = fields.String(
        allow_none=True, description="Command to execute (command or execution script is required)."
    )
    use_execution_script = fields.Bool(
        allow_none=True,
        description="Whether to run task with the execution command or the execution script.",
    )
    execution_script_storage_id = IdReference(
        referenced_class="File",
        allow_none=True,
        description="Script to execute (command or execution script is required).",
    )

    input_files = fields.Nested(FileSchema, many=True, allow_none=True)
    output_files = fields.Nested(FileSchema, many=True, allow_none=True)
