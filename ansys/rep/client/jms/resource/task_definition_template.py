# autogenerated code
from marshmallow.utils import missing
from ansys.rep.client.common import Object
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

    """

    class Meta:
        schema = TemplatePropertySchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.default = missing
        self.description = missing
        self.type = missing

        super().__init__(**kwargs)

TemplatePropertySchema.Meta.object_class = TemplateProperty

class TemplateResourceRequirements(Object):
    """TemplateResourceRequirements resource.

    Parameters
    ----------
    platform : TemplateProperty, optional
    memory : TemplateProperty, optional
    cpu_core_usage : TemplateProperty, optional
    disk_space : TemplateProperty, optional
    custom : dict, optional

    """

    class Meta:
        schema = TemplateResourceRequirementsSchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.platform = missing
        self.memory = missing
        self.cpu_core_usage = missing
        self.disk_space = missing
        self.custom = missing

        super().__init__(**kwargs)

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

    """

    class Meta:
        schema = TemplateInputFileSchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.name = missing
        self.type = missing
        self.evaluation_path = missing
        self.description = missing

        super().__init__(**kwargs)

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
    monitor : bool, optional
        Should the file's contents be live monitored
    collect : bool, optional
        Should files be collected per job

    """

    class Meta:
        schema = TemplateOutputFileSchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.name = missing
        self.type = missing
        self.evaluation_path = missing
        self.description = missing
        self.monitor = missing
        self.collect = missing

        super().__init__(**kwargs)

TemplateOutputFileSchema.Meta.object_class = TemplateOutputFile

class TaskDefinitionTemplate(Object):
    """TaskDefinitionTemplate resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    modification_time : datetime, optional
        Last time the object was modified, in UTC
    creation_time : datetime, optional
        Time when the object was created, in UTC
    name : str
        Name of the template
    version : str, optional
        version of the template
    software_requirements : Software, optional
        A list of required software.
    resource_requirements : TemplateResourceRequirements, optional
        Includes hardware requirements such as number of cores, memory and disk space.
    execution_context : dict, optional
        Additional arguments to pass to the executing command
    environment : dict, optional
        Environment variables to set for the executed process
    execution_command : str, optional
        Command to execute (command or execution script is required).
    use_execution_script : bool, optional
        Whether to run task with the execution command or the execution script.
    execution_script_storage_id : str, optional
        Storage ID of the script to execute (command or execution script is required).
    input_files : TemplateInputFile, optional
        List of predefined input files.
    output_files : TemplateOutputFile, optional
        List of predefined output files.

    """

    class Meta:
        schema = TaskDefinitionTemplateSchema
        rest_name = "task_definition_templates"

    def __init__(self, **kwargs):
        self.id = missing
        self.modification_time = missing
        self.creation_time = missing
        self.name = missing
        self.version = missing
        self.software_requirements = missing
        self.resource_requirements = missing
        self.execution_context = missing
        self.environment = missing
        self.execution_command = missing
        self.use_execution_script = missing
        self.execution_script_storage_id = missing
        self.input_files = missing
        self.output_files = missing

        super().__init__(**kwargs)

TaskDefinitionTemplateSchema.Meta.object_class = TaskDefinitionTemplate
