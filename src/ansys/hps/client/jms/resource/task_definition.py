# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
# autogenerated code
from marshmallow.utils import missing

from ansys.hps.client.common import Object

from ..schema.task_definition import (
    HpcResourcesSchema,
    LicensingSchema,
    ResourceRequirementsSchema,
    SoftwareSchema,
    SuccessCriteriaSchema,
    TaskDefinitionSchema,
)


class HpcResources(Object):
    """Provides the HPC resource.

    Parameters
    ----------
    num_cores_per_node : int, optional
        Number of cores per node.
    num_gpus_per_node : int, optional
        Number of GPUs per node.
    exclusive : bool, optional
        Whether a job can't share resources with other running jobs.
    queue : str, optional
        Name of the job scheduler queue.
    """

    class Meta:
        schema = HpcResourcesSchema
        rest_name = "None"

    def __init__(
        self,
        num_cores_per_node=missing,
        num_gpus_per_node=missing,
        exclusive=missing,
        queue=missing,
        **kwargs
    ):
        self.num_cores_per_node = num_cores_per_node
        self.num_gpus_per_node = num_gpus_per_node
        self.exclusive = exclusive
        self.queue = queue

        self.obj_type = self.__class__.__name__


HpcResourcesSchema.Meta.object_class = HpcResources


class ResourceRequirements(Object):
    """Provides the resource requirements resource.

    Parameters
    ----------
    platform : str, optional
        Basic platform information. Options are ``'linux'`` and ``'windows'``.
    memory : int, optional
        Amount of RAM in bytes.
    num_cores : float, optional
        Number of cores.
    disk_space : int, optional
        Amount of disk space in bytes.
    distributed : bool, optional
        Whether to enable distributed parallel processing.
    custom : dict[str, int | float | str | bool], optional
        Dictionary of custom resource requirements.
    hpc_resources : HpcResources, optional
        HPC resources.
    """

    class Meta:
        schema = ResourceRequirementsSchema
        rest_name = "None"

    def __init__(
        self,
        platform=missing,
        memory=missing,
        num_cores=missing,
        disk_space=missing,
        distributed=missing,
        custom=missing,
        hpc_resources=missing,
        **kwargs
    ):
        self.platform = platform
        self.memory = memory
        self.num_cores = num_cores
        self.disk_space = disk_space
        self.distributed = distributed
        self.custom = custom
        self.hpc_resources = hpc_resources

        self.obj_type = self.__class__.__name__


ResourceRequirementsSchema.Meta.object_class = ResourceRequirements


class Software(Object):
    """Provides the software resource.

    Parameters
    ----------
    name : str
        Name of the app.
    version : str, optional
        Version of the app.

    """

    class Meta:
        schema = SoftwareSchema
        rest_name = "None"

    def __init__(self, name=missing, version=missing, **kwargs):
        self.name = name
        self.version = version

        self.obj_type = self.__class__.__name__


SoftwareSchema.Meta.object_class = Software


class SuccessCriteria(Object):
    """Provides the success criteria resource.

    Parameters
    ----------
    return_code : int, optional
        Process exit code that must be returned by the executed command.
    expressions : list, optional
        List of expressions to evaluate.
    required_output_file_ids : list[str], optional
        List of IDs of the required output files.
    require_all_output_files : bool, optional
        Whether to require all output files.
    required_output_parameter_ids : list[str], optional
        List of names of the required output parameters.
    require_all_output_parameters : bool, optional
        Whether to require all output parameters.
    """

    class Meta:
        schema = SuccessCriteriaSchema
        rest_name = "None"

    def __init__(
        self,
        return_code=missing,
        expressions=missing,
        required_output_file_ids=missing,
        require_all_output_files=missing,
        required_output_parameter_ids=missing,
        require_all_output_parameters=missing,
        **kwargs
    ):
        self.return_code = return_code
        self.expressions = expressions
        self.required_output_file_ids = required_output_file_ids
        self.require_all_output_files = require_all_output_files
        self.required_output_parameter_ids = required_output_parameter_ids
        self.require_all_output_parameters = require_all_output_parameters

        self.obj_type = self.__class__.__name__


SuccessCriteriaSchema.Meta.object_class = SuccessCriteria


class Licensing(Object):
    """Provides the licensing resource.

    Parameters
    ----------
    enable_shared_licensing : bool, optional
        Whether to enable shared licensing contexts for Ansys simulations.

    """

    class Meta:
        schema = LicensingSchema
        rest_name = "None"

    def __init__(self, enable_shared_licensing=missing, **kwargs):
        self.enable_shared_licensing = enable_shared_licensing

        self.obj_type = self.__class__.__name__


LicensingSchema.Meta.object_class = Licensing


class TaskDefinition(Object):
    """Provides the task definition resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    creation_time : datetime, optional
        Date and time that the resource was created.
    modification_time : datetime, optional
        Date and time that the resource was last modified.
    created_by : str, optional
        ID of the user who created the object.
    modified_by : str, optional
        ID of the user who last modified the object.
    name : str, optional
        Name.
    execution_command : str, optional
        Command to execute. A command or execution script is required.
    use_execution_script : bool, optional
        Whether to run the task with the execution script or the execution command.
    execution_script_id : str, optional
        Script to execute. A command or execution script is required.
    execution_level : int
        Execution level for the task.
    execution_context : dict[str, int | float | str | bool], optional
        Additional arguments to pass to the executing command.
    environment : dict[str, str], optional
        Environment variables to set for the executed process.
    max_execution_time : float, optional
        Maximum time in seconds for executing the task.
    num_trials : int, optional
        Maximum number of attempts for executing the task.
    store_output : bool, optional
        Whether to store the standard output of the task.
    input_file_ids : list[str]
        List of IDs of input files.
    output_file_ids : list[str]
        List of IDs of output files.
    success_criteria : SuccessCriteria, optional
    licensing : Licensing, optional
        :class:`Licensing` object.
    software_requirements : list[Software], optional
        List of :class:`Software` objects.
    resource_requirements : ResourceRequirements, optional
        :class:`ResourceRequirements` object.
    """

    class Meta:
        schema = TaskDefinitionSchema
        rest_name = "task_definitions"

    def __init__(
        self,
        id=missing,
        creation_time=missing,
        modification_time=missing,
        created_by=missing,
        modified_by=missing,
        name=missing,
        execution_command=missing,
        use_execution_script=missing,
        execution_script_id=missing,
        execution_level=missing,
        execution_context=missing,
        environment=missing,
        max_execution_time=missing,
        num_trials=missing,
        store_output=missing,
        input_file_ids=missing,
        output_file_ids=missing,
        success_criteria=missing,
        licensing=missing,
        software_requirements=missing,
        resource_requirements=missing,
        **kwargs
    ):
        self.id = id
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.name = name
        self.execution_command = execution_command
        self.use_execution_script = use_execution_script
        self.execution_script_id = execution_script_id
        self.execution_level = execution_level
        self.execution_context = execution_context
        self.environment = environment
        self.max_execution_time = max_execution_time
        self.num_trials = num_trials
        self.store_output = store_output
        self.input_file_ids = input_file_ids
        self.output_file_ids = output_file_ids
        self.success_criteria = success_criteria
        self.licensing = licensing
        self.software_requirements = software_requirements
        self.resource_requirements = resource_requirements

        self.obj_type = self.__class__.__name__


TaskDefinitionSchema.Meta.object_class = TaskDefinition
