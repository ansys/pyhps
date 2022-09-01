
from marshmallow.utils import missing
from .base import Object
from ..schema.task_definition import TaskDefinitionSchema

class TaskDefinition(Object):
    """TaskDefinition resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        name (str, optional): Name.
        execution_command (str, optional): Command to execute (command or execution script is required).
        use_execution_script (bool, optional): Whether to run task with the execution command or the execution script.
        execution_script_id (str, optional): Script to execute (command or execution script is required).
        execution_level (int): Define execution level for this task.
        execution_context (dict, optional): Additional arguments to pass to the executing command
        environment (dict, optional): Environment variables to set for the executed process
        max_execution_time (float, optional): Maximum time in seconds for executing the task.
        num_trials (int, optional): Maximum number of attempts to execute the task.
        store_output (bool, optional): Specify whether to store the standard output of the task.
        input_file_ids (list): List of IDs of input files.
        output_file_ids (list): List of IDs of output files.
        success_criteria (optional): A :class:`ansys.rep.client.jms.SuccessCriteria` object.
        licensing (optional): A :class:`ansys.rep.client.jms.Licensing` object.
        software_requirements (optional): A list of :class:`ansys.rep.client.jms.Software` objects.
        resource_requirements (optional): A :class:`ansys.rep.client.jms.ResourceRequirements` object.

    """

    class Meta:
        schema = TaskDefinitionSchema
        rest_name = "task_definitions"

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.execution_command = missing
        self.use_execution_script = missing
        self.execution_script_id = missing
        self.execution_level = missing
        self.execution_context = missing
        self.environment = missing
        self.max_execution_time = missing
        self.num_trials = missing
        self.store_output = missing
        self.input_file_ids = missing
        self.output_file_ids = missing
        self.success_criteria = missing
        self.licensing = missing
        self.software_requirements = missing
        self.resource_requirements = missing

        super().__init__(**kwargs)

TaskDefinitionSchema.Meta.object_class = TaskDefinition
