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
"""Module providing task definition related schemas."""

from marshmallow import fields

from ansys.hps.client.common import BaseSchema, ObjectSchemaWithModificationInfo, RestrictedValue

from .object_reference import IdReference, IdReferenceList


class SoftwareSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    name = fields.String(metadata={"description": "Name of the app."})
    version = fields.String(allow_none=True, metadata={"description": "Version of the app."})


class HpcResourcesSchema(BaseSchema):
    class Meta:
        pass

    num_cores_per_node = fields.Int(
        allow_none=True, metadata={"description": "Number of cores per node."}
    )
    num_gpus_per_node = fields.Int(
        allow_none=True, metadata={"description": "Number of GPUs per node."}
    )
    exclusive = fields.Bool(
        allow_none=True,
        metadata={"description": "Whether a job can't share resources with other running jobs."},
    )
    queue = fields.Str(
        allow_none=True, metadata={"description": "Name of the job scheduler queue."}
    )
    use_local_scratch = fields.Bool(
        allow_none=True,
        metadata={"description": "Whether to use node local storage."},
    )
    native_submit_options = fields.Str(
        allow_none=True,
        metadata={
            "description": "Additional command line options to pass directly to the scheduler."
        },
    )
    custom_orchestration_options = fields.Dict(
        allow_none=True,
        keys=fields.Str(),
        values=RestrictedValue(),
        metadata={"description": "Dictionary of custom orchestration options."},
    )


class WorkerContextSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    max_runtime = fields.Int(
        allow_none=True,
        metadata={"description": "Maximum run time (in seconds) for an ephemeral evaluator."},
    )
    max_num_parallel_tasks = fields.Int(
        allow_none=True,
        metadata={
            "description": "Maximum number of tasks that "
            "an ephemeral evaluator can run in parallel."
        },
    )


class ResourceRequirementsSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    platform = fields.String(
        allow_none=True,
        metadata={
            "description": "Basic platform information. Options are ``'linux'`` and ``'windows'``."
        },
    )
    memory = fields.Int(allow_none=True, metadata={"description": "Amount of RAM in bytes."})
    num_cores = fields.Float(allow_none=True, metadata={"description": "Number of cores."})
    disk_space = fields.Int(
        allow_none=True, metadata={"description": "Amount of disk space in bytes."}
    )
    distributed = fields.Bool(
        allow_none=True,
        metadata={"description": "Whether to enable distributed parallel processing."},
    )
    compute_resource_set_id = fields.String(
        allow_none=True,
        metadata={"description": "ID of the compute resource set that this task should run on."},
    )
    evaluator_id = fields.String(
        allow_none=True,
        metadata={"description": "ID of the evaluator that this task should run on."},
    )
    custom = fields.Dict(
        allow_none=True,
        keys=fields.Str(),
        values=RestrictedValue(),
        metadata={"description": "Dictionary of custom resource requirements."},
    )
    hpc_resources = fields.Nested(
        HpcResourcesSchema, allow_none=True, metadata={"description": "HPC resource requirements."}
    )


class SuccessCriteriaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    return_code = fields.Int(
        allow_none=True,
        metadata={
            "description": "Process exit code that must be returned by the executed command."
        },
    )
    expressions = fields.List(
        fields.String(),
        allow_none=True,
        metadata={"description": "List of expressions to evaluate."},
    )

    required_output_file_ids = IdReferenceList(
        "File",
        attribute="required_output_file_ids",
        allow_none=True,
        metadata={"description": "List of IDs of the required output files."},
    )
    require_all_output_files = fields.Bool(
        allow_none=True, metadata={"description": "Whether to require all output files."}
    )

    required_output_parameter_ids = IdReferenceList(
        "ParameterDefinition",
        attribute="required_output_parameter_ids",
        allow_none=True,
        metadata={"description": "List of names of the required output parameters."},
    )
    require_all_output_parameters = fields.Bool(
        allow_none=True, metadata={"description": "Whether to require all output parameters."}
    )


class LicensingSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        pass

    enable_shared_licensing = fields.Bool(
        allow_none=True,
        metadata={
            "description": "Whether to enable shared licensing contexts for Ansys simulations."
        },
    )


class TaskDefinitionSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(allow_none=True, metadata={"description": "Name."})

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
    execution_script_id = IdReference(
        referenced_class="File",
        allow_none=True,
        metadata={"description": "Script to execute. A command or execution script is required."},
    )

    execution_level = fields.Int(metadata={"description": "Execution level for the task."})
    execution_context = fields.Dict(
        allow_none=True,
        metadata={"description": "Additional arguments to pass to the executing command."},
        keys=fields.Str(),
        values=RestrictedValue(),
    )
    environment = fields.Dict(
        allow_none=True,
        metadata={"description": "Environment variables to set for the executed process."},
        keys=fields.Str(),
        values=fields.Str(),
    )
    max_execution_time = fields.Float(
        allow_none=True, metadata={"description": "Maximum time in seconds for executing the task."}
    )
    num_trials = fields.Int(
        allow_none=True,
        metadata={"description": "Maximum number of attempts for executing the task."},
    )
    store_output = fields.Bool(
        allow_none=True,
        metadata={"description": "Whether to store the standard output of the task."},
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
        metadata={"description": ":class:`Licensing` object."},
    )

    software_requirements = fields.Nested(
        SoftwareSchema,
        many=True,
        allow_none=True,
        metadata={"description": "List of :class:`Software` objects."},
    )
    resource_requirements = fields.Nested(
        ResourceRequirementsSchema,
        allow_none=True,
        metadata={"description": ":class:`ResourceRequirements` object."},
    )
    worker_context = fields.Nested(
        WorkerContextSchema,
        allow_none=True,
        metadata={"description": ":class:`WorkerContext` object."},
    )
