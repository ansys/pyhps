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
from ..schema.task_definition_template import TemplatePropertySchema
from ..schema.task_definition_template import TemplateResourceRequirementsSchema
from ..schema.task_definition_template import TemplateInputFileSchema
from ..schema.task_definition_template import TemplateOutputFileSchema
from ..schema.task_definition_template import TaskDefinitionTemplateSchema

class TemplateProperty(Object):
    """TemplateProperty resource.

    Parameters
    ----------
    default : any, optional
        Default value.
    description : str, optional
        Description of the property's purpose.
    type : str, optional
        Type of the property: either int, float, bool or string.
    value_list : any, optional
        List of possible values for this property.

    """

    class Meta:
        schema = TemplatePropertySchema
        rest_name = "None"

    def __init__(self,
        default=missing,
        description=missing,
        type=missing,
        value_list=missing,
        **kwargs
    ):
        self.default = default
        self.description = description
        self.type = type
        self.value_list = value_list

        self.obj_type = self.__class__.__name__

TemplatePropertySchema.Meta.object_class = TemplateProperty

class TemplateResourceRequirements(Object):
    """TemplateResourceRequirements resource.

    Parameters
    ----------
    platform : TemplateProperty, optional
    memory : TemplateProperty, optional
    num_cores : TemplateProperty, optional
    disk_space : TemplateProperty, optional
    distributed : TemplateProperty, optional
    custom : dict[str, TemplateProperty], optional
    hpc_resources : HpcResources, optional

    """

    class Meta:
        schema = TemplateResourceRequirementsSchema
        rest_name = "None"

    def __init__(self,
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

TemplateResourceRequirementsSchema.Meta.object_class = TemplateResourceRequirements

class TemplateInputFile(Object):
    """TemplateInputFile resource.

    Parameters
    ----------
    name : str
        Name of the file.
    type : str, optional
        MIME type of the file, ie. text/plain.
    evaluation_path : str, optional
        Path under which the file is expected to be found during evaluation.
    description : str
        Description of the file's purpose.
    required : bool
        Is the file required by the task

    """

    class Meta:
        schema = TemplateInputFileSchema
        rest_name = "None"

    def __init__(self,
        name=missing,
        type=missing,
        evaluation_path=missing,
        description=missing,
        required=missing,
        **kwargs
    ):
        self.name = name
        self.type = type
        self.evaluation_path = evaluation_path
        self.description = description
        self.required = required

        self.obj_type = self.__class__.__name__

TemplateInputFileSchema.Meta.object_class = TemplateInputFile

class TemplateOutputFile(Object):
    """TemplateOutputFile resource.

    Parameters
    ----------
    name : str
        Name of the file.
    type : str, optional
        MIME type of the file, ie. text/plain.
    evaluation_path : str, optional
        Path under which the file is expected to be found during evaluation.
    description : str
        Description of the file's purpose.
    required : bool
        Is the file required by the task
    monitor : bool, optional
        Should the file's contents be live monitored.
    collect : bool, optional
        Should files be collected per job.

    """

    class Meta:
        schema = TemplateOutputFileSchema
        rest_name = "None"

    def __init__(self,
        name=missing,
        type=missing,
        evaluation_path=missing,
        description=missing,
        required=missing,
        monitor=missing,
        collect=missing,
        **kwargs
    ):
        self.name = name
        self.type = type
        self.evaluation_path = evaluation_path
        self.description = description
        self.required = required
        self.monitor = monitor
        self.collect = collect

        self.obj_type = self.__class__.__name__

TemplateOutputFileSchema.Meta.object_class = TemplateOutputFile

class TaskDefinitionTemplate(Object):
    """TaskDefinitionTemplate resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    modification_time : datetime, optional
        Last time the object was modified, in UTC.
    creation_time : datetime, optional
        Time when the object was created, in UTC.
    name : str
        Name of the template
    version : str, optional
        Version of the template
    description : str, optional
        Description of the template
    software_requirements : list[Software], optional
        A list of required software.
    resource_requirements : TemplateResourceRequirements, optional
        Includes hardware requirements such as number of cores, memory and disk space.
    execution_context : dict[str, TemplateProperty], optional
        Additional arguments to pass to the executing command.
    environment : dict[str, TemplateProperty], optional
        Environment variables to set for the executed process.
    execution_command : str, optional
        Command to execute (command or execution script is required).
    use_execution_script : bool, optional
        Whether to run task with the execution command or the execution script.
    execution_script_storage_id : str, optional
        Storage ID of the script to execute (command or execution script is required).
    execution_script_storage_bucket : str, optional
        File storage bucket where the execution script is located.
    input_files : list[TemplateInputFile], optional
        List of predefined input files.
    output_files : list[TemplateOutputFile], optional
        List of predefined output files.

    """

    class Meta:
        schema = TaskDefinitionTemplateSchema
        rest_name = "task_definition_templates"

    def __init__(self,
        id=missing,
        modification_time=missing,
        creation_time=missing,
        name=missing,
        version=missing,
        description=missing,
        software_requirements=missing,
        resource_requirements=missing,
        execution_context=missing,
        environment=missing,
        execution_command=missing,
        use_execution_script=missing,
        execution_script_storage_id=missing,
        execution_script_storage_bucket=missing,
        input_files=missing,
        output_files=missing,
        **kwargs
    ):
        self.id = id
        self.modification_time = modification_time
        self.creation_time = creation_time
        self.name = name
        self.version = version
        self.description = description
        self.software_requirements = software_requirements
        self.resource_requirements = resource_requirements
        self.execution_context = execution_context
        self.environment = environment
        self.execution_command = execution_command
        self.use_execution_script = use_execution_script
        self.execution_script_storage_id = execution_script_storage_id
        self.execution_script_storage_bucket = execution_script_storage_bucket
        self.input_files = input_files
        self.output_files = output_files

        self.obj_type = self.__class__.__name__

TaskDefinitionTemplateSchema.Meta.object_class = TaskDefinitionTemplate
