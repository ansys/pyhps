# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from ansys.rep.client.common import BaseSchema, ObjectSchemaWithModificationInfo, RestrictedValue
from marshmallow import fields

from .object_reference import IdReference, IdReferenceList


class SoftwareSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    name = fields.String(metadata={"description": "Application's name."})
    version = fields.String(allow_none=True, metadata={"description": "Application's version."})


class HpcResourcesSchema(BaseSchema):
    class Meta:
        pass

    num_cores_per_node = fields.Int(allow_none=True)
    num_gpus_per_node = fields.Int(allow_none=True)
    exclusive = fields.Bool(allow_none=True)
    queue = fields.Str(allow_none=True)


class ResourceRequirementsSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    platform = fields.String(allow_none=True)
    memory = fields.Int(allow_none=True)
    num_cores = fields.Float(allow_none=True)
    disk_space = fields.Int(allow_none=True)
    distributed = fields.Bool(allow_none=True)
    custom = fields.Dict(allow_none=True, keys=fields.Str(), values=RestrictedValue())
    hpc_resources = fields.Nested(HpcResourcesSchema, allow_none=True)


class SuccessCriteriaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    return_code = fields.Int(
        allow_none=True,
        metadata={
            "description": "The process exit code that must be returned by the executed command."
        },
    )
    expressions = fields.List(
        fields.String(),
        allow_none=True,
        metadata={"description": "A list of expressions to be evaluated."},
    )

    required_output_file_ids = IdReferenceList(
        "File",
        attribute="required_output_file_ids",
        allow_none=True,
        metadata={"description": "List of IDs of required output files."},
    )
    require_all_output_files = fields.Bool(
        allow_none=True, metadata={"description": "Flag to require all output files."}
    )

    required_output_parameter_ids = IdReferenceList(
        "ParameterDefinition",
        attribute="required_output_parameter_ids",
        allow_none=True,
        metadata={"description": "List of names of required output parameters."},
    )
    require_all_output_parameters = fields.Bool(
        allow_none=True, metadata={"description": "Flag to require all output parameters."}
    )


class LicensingSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    enable_shared_licensing = fields.Bool(
        allow_none=True,
        metadata={
            "description": "Whether to enable shared licensing contexts for Ansys simulations"
        },
    )


class TaskDefinitionSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(allow_none=True, metadata={"description": "Name."})

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
    execution_script_id = IdReference(
        referenced_class="File",
        allow_none=True,
        metadata={"description": "Script to execute (command or execution script is required)."},
    )

    execution_level = fields.Int(metadata={"description": "Define execution level for this task."})
    execution_context = fields.Dict(
        allow_none=True,
        metadata={"description": "Additional arguments to pass to the executing command"},
        keys=fields.Str(),
        values=RestrictedValue(),
    )
    environment = fields.Dict(
        allow_none=True,
        metadata={"description": "Environment variables to set for the executed process"},
        keys=fields.Str(),
        values=fields.Str(),
    )
    max_execution_time = fields.Float(
        allow_none=True, metadata={"description": "Maximum time in seconds for executing the task."}
    )
    num_trials = fields.Int(
        allow_none=True, metadata={"description": "Maximum number of attempts to execute the task."}
    )
    store_output = fields.Bool(
        allow_none=True,
        metadata={"description": "Specify whether to store the standard output of the task."},
    )

    input_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="input_file_ids",
        metadata={"description": "List of IDs of input files."},
    )
    output_file_ids = IdReferenceList(
        referenced_class="File",
        attribute="output_file_ids",
        metadata={"description": "List of IDs of output files."},
    )

    success_criteria = fields.Nested(
        SuccessCriteriaSchema,
        allow_none=True,
    )
    licensing = fields.Nested(
        LicensingSchema,
        allow_none=True,
        metadata={"description": "A :class:`Licensing` object."},
    )

    software_requirements = fields.Nested(
        SoftwareSchema,
        many=True,
        allow_none=True,
        metadata={"description": "A list of :class:`Software` objects."},
    )
    resource_requirements = fields.Nested(
        ResourceRequirementsSchema,
        allow_none=True,
        metadata={"description": "A :class:`ResourceRequirements` object."},
    )