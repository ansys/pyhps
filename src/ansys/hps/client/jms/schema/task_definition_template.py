# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F. Negri
# ----------------------------------------------------------

from marshmallow import fields, validate

from ansys.hps.client.common import BaseSchema, ObjectSchema

from .task_definition import HpcResourcesSchema, SoftwareSchema


class TemplatePropertySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    default = fields.Raw(allow_none=True, metadata={"description": "Default value."})
    description = fields.String(
        allow_none=True, metadata={"description": "Description of the property's purpose."}
    )
    type = fields.String(
        allow_none=True,
        validate=validate.OneOf(["int", "float", "bool", "string"]),
        metadata={"description": "Type of the property: either int, float, bool or string."},
    )
    value_list = fields.Raw(
        allow_none=True,
        dump_default=[],
        load_default=[],
        metadata={"many": True, "description": "List of possible values for this property."},
    )


class TemplateResourceRequirementsSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    platform = fields.Nested(TemplatePropertySchema, allow_none=True)
    memory = fields.Nested(TemplatePropertySchema, allow_none=True)
    num_cores = fields.Nested(TemplatePropertySchema, allow_none=True)
    disk_space = fields.Nested(TemplatePropertySchema, allow_none=True)
    distributed = fields.Nested(TemplatePropertySchema, allow_none=True)
    custom = fields.Dict(
        keys=fields.String, values=fields.Nested(TemplatePropertySchema), allow_none=True
    )
    hpc_resources = fields.Nested(HpcResourcesSchema, allow_none=True)


class TemplateFileSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    name = fields.String(metadata={"description": "Name of the file."})
    type = fields.String(
        allow_none=True, metadata={"description": "MIME type of the file, ie. text/plain."}
    )
    evaluation_path = fields.String(
        allow_none=True,
        metadata={
            "description": "Path under which the file is expected to be found during evaluation."
        },
    )
    description = fields.String(metadata={"description": "Description of the file's purpose."})
    required = fields.Bool(metadata={"description": "Is the file required by the task"})


class TemplateInputFileSchema(TemplateFileSchema):
    pass


class TemplateOutputFileSchema(TemplateFileSchema):
    monitor = fields.Bool(
        allow_none=True, metadata={"description": "Should the file's contents be live monitored."}
    )
    collect = fields.Bool(
        allow_none=True, metadata={"description": "Should files be collected per job."}
    )


class TaskDefinitionTemplateSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Last time the object was modified, in UTC."},
    )
    creation_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Time when the object was created, in UTC."},
    )

    name = fields.String(metadata={"description": "Name of the template"})
    version = fields.String(metadata={"description": "Version of the template"}, allow_none=True)
    description = fields.String(
        metadata={"description": "Description of the template"}, allow_none=True
    )

    software_requirements = fields.Nested(
        SoftwareSchema,
        many=True,
        allow_none=True,
        metadata={"description": "A list of required software."},
    )
    resource_requirements = fields.Nested(
        TemplateResourceRequirementsSchema,
        allow_none=True,
        metadata={
            "description": "Includes hardware requirements such as number of cores,"
            " memory and disk space."
        },
    )

    execution_context = fields.Dict(
        keys=fields.String,
        values=fields.Nested(TemplatePropertySchema),
        allow_none=True,
        metadata={"description": "Additional arguments to pass to the executing command."},
    )
    environment = fields.Dict(
        keys=fields.String,
        values=fields.Nested(TemplatePropertySchema),
        allow_none=True,
        metadata={"description": "Environment variables to set for the executed process."},
    )

    execution_command = fields.String(
        allow_none=True,
        metadata={"description": "Command to execute (command or execution script is required)."},
    )
    use_execution_script = fields.Bool(
        allow_none=True,
        metadata={
            "description": "Whether to run task with the execution command or the execution script."
        },
    )
    execution_script_storage_id = fields.String(
        allow_none=True,
        metadata={
            "description": "Storage ID of the script to execute "
            "(command or execution script is required).",
        },
    )
    execution_script_storage_bucket = fields.String(
        allow_none=True,
        metadata={"description": "File storage bucket where the execution script is located."},
    )

    input_files = fields.Nested(
        TemplateInputFileSchema,
        many=True,
        allow_none=True,
        metadata={"description": "List of predefined input files."},
    )
    output_files = fields.Nested(
        TemplateOutputFileSchema,
        many=True,
        allow_none=True,
        metadata={"description": "List of predefined output files."},
    )
