# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides task definition template related schemas."""

from marshmallow import fields, validate

from ansys.hps.client.common import BaseSchema, ObjectSchema

from .task_definition import HpcResourcesSchema, SoftwareSchema, WorkerContextSchema


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
        metadata={
            "description": "Type of the property. "
            "Options are ``bool``, ``float``, ``int``, and ``string``."
        },
    )
    value_list = fields.Raw(
        allow_none=True,
        dump_default=[],
        load_default=[],
        metadata={"many": True, "description": "List of possible values for the property."},
    )


class TemplateResourceRequirementsSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    platform = fields.Nested(TemplatePropertySchema, allow_none=True)
    memory = fields.Nested(TemplatePropertySchema, allow_none=True)
    num_cores = fields.Nested(TemplatePropertySchema, allow_none=True)
    disk_space = fields.Nested(TemplatePropertySchema, allow_none=True)
    distributed = fields.Nested(TemplatePropertySchema, allow_none=True)
    compute_resource_set_id = fields.Nested(TemplatePropertySchema, allow_none=True)
    evaluator_id = fields.Nested(TemplatePropertySchema, allow_none=True)
    custom = fields.Dict(
        keys=fields.String, values=fields.Nested(TemplatePropertySchema), allow_none=True
    )
    hpc_resources = fields.Nested(HpcResourcesSchema, allow_none=True)


class TemplateFileSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    name = fields.String(metadata={"description": "Name of the file."})
    type = fields.String(
        allow_none=True,
        metadata={"description": "MIME type of the file. For example, ``text/plain``."},
    )
    evaluation_path = fields.String(
        allow_none=True,
        metadata={
            "description": "Path that the file is expected to be found under during evaluation."
        },
    )
    description = fields.String(metadata={"description": "Description of the file's purpose."})
    required = fields.Bool(metadata={"description": "Whether the file is required by the task."})


class TemplateInputFileSchema(TemplateFileSchema):
    pass


class TemplateOutputFileSchema(TemplateFileSchema):
    monitor = fields.Bool(
        allow_none=True, metadata={"description": "Whether to live monitor the file's contents."}
    )
    collect = fields.Bool(
        allow_none=True, metadata={"description": "Whether to collect files per job."}
    )


class TaskDefinitionTemplateSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    modification_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={
            "description": "Last time in UTC (Coordinated Universal Time) "
            "that the object was modified."
        },
    )
    creation_time = fields.DateTime(
        allow_none=True,
        load_only=True,
        metadata={"description": "Time in UTC when the object was created."},
    )

    name = fields.String(metadata={"description": "Name of the template."})
    version = fields.String(metadata={"description": "Version of the template."}, allow_none=True)
    description = fields.String(
        metadata={"description": "Description of the template."}, allow_none=True
    )

    software_requirements = fields.Nested(
        SoftwareSchema,
        many=True,
        allow_none=True,
        metadata={"description": "List of required software."},
    )
    resource_requirements = fields.Nested(
        TemplateResourceRequirementsSchema,
        allow_none=True,
        metadata={
            "description": "Hardware requirements such as the number of cores, "
            "memory, and disk space."
        },
    )
    worker_context = fields.Nested(
        WorkerContextSchema,
        allow_none=True,
        metadata={"description": ":class:`WorkerContext` object."},
    )

    execution_context = fields.Dict(
        keys=fields.String,
        values=fields.Nested(TemplatePropertySchema),
        allow_none=True,
        metadata={
            "description": "Dictionary of additional arguments to pass to the executing command."
        },
    )
    environment = fields.Dict(
        keys=fields.String,
        values=fields.Nested(TemplatePropertySchema),
        allow_none=True,
        metadata={
            "description": "Dictionary of environment variables to set for the executed process."
        },
    )

    execution_command = fields.String(
        allow_none=True,
        metadata={"description": "Command to execute. A command or execution script is required."},
    )
    use_execution_script = fields.Bool(
        allow_none=True,
        metadata={
            "description": "Whether to run the task with the execution script "
            "or the execution command."
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
