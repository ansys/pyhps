# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields

from .base import BaseSchema, ObjectSchema
from .object_reference import IdReference, IdReferenceList


class SoftwareSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    name = fields.String()
    version = fields.String(allow_none=True)


class ResourceRequirementsSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    platform = fields.String(allow_none=True)
    memory = fields.Int(allow_none=True)
    cpu_core_usage = fields.Float(allow_none=True)
    disk_space = fields.Int(allow_none=True)

    user_data = fields.Dict(allow_none=True)


class SuccessCriteriaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    return_code = fields.Int(
        allow_none=True,
        description="The process exit code that must be returned by the executed command.",
    )
    expressions = fields.List(
        fields.String(), allow_none=True, description="A list of expressions to be evaluated."
    )

    required_output_files = IdReferenceList(
        "File",
        attribute="required_output_file_ids",
        allow_none=True,
        description="List of IDs of required output files.",
    )
    require_all_output_files = fields.Bool(
        allow_none=True, description="Flag to require all output files."
    )

    required_output_parameters = IdReferenceList(
        "ParameterDefinition",
        attribute="required_output_parameter_ids",
        allow_none=True,
        description="List of names of required output parameters.",
    )
    require_all_output_parameters = fields.Bool(
        allow_none=True, description="Flag to require all output parameters."
    )


class LicensingSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    enable_shared_licensing = fields.Bool(
        allow_none=True,
        description="Whether to enable shared licensing contexts for Ansys simulations",
    )


class TaskDefinitionSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    name = fields.String(allow_none=True, description="Name.")

    execution_command = fields.String(
        allow_none=True, description="Command to execute (command or execution script is required)."
    )
    use_execution_script = fields.Bool(
        allow_none=True,
        description="Whether to run task with the execution command or the execution script.",
    )
    execution_script_id = IdReference(
        referenced_class="File",
        allow_none=True,
        description="Script to execute (command or execution script is required).",
    )

    execution_level = fields.Int(description="Define execution level for this task.")
    execution_context = fields.Dict(
        allow_none=True, description="Additional arguments to pass to the executing command"
    )
    environment = fields.Dict(
        allow_none=True, description="Environment variables to set for the executed process"
    )
    max_execution_time = fields.Float(
        allow_none=True, description="Maximum time in seconds for executing the task."
    )
    num_trials = fields.Int(
        allow_none=True, description="Maximum number of attempts to execute the task."
    )
    store_output = fields.Bool(
        allow_none=True,
        description="Specify whether to store the standard output of the task.",
    )

    input_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="input_file_ids",
        description="List of IDs of input files.",
    )
    output_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="output_file_ids",
        description="List of IDs of output files.",
    )

    success_criteria = fields.Nested(
        SuccessCriteriaSchema,
        allow_none=True,
        description="A :class:`ansys.rep.client.jms.SuccessCriteria` object.",
    )
    licensing = fields.Nested(
        LicensingSchema,
        allow_none=True,
        description="A :class:`ansys.rep.client.jms.Licensing` object.",
    )

    software_requirements = fields.Nested(SoftwareSchema, many=True, allow_none=True)
    resource_requirements = fields.Nested(ResourceRequirementsSchema, allow_none=True)
