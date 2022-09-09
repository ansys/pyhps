# autogenerated code based on TaskDefinitionTemplateSchema

from marshmallow.utils import missing
from ansys.rep.client.common import Object
from ..schema.task_definition_template import TaskDefinitionTemplateSchema

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
    software_requirements : object, optional
    resource_requirements : object, optional
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
    input_files : object, optional
    output_files : object, optional

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
