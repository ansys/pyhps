
from marshmallow.utils import missing
from .base import Object
from ..schema.task import TaskSchema

class Task(Object):
    """Task resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        modification_time (datetime, optional): The date and time the task was last modified.
        creation_time (datetime, optional): The date and time the task was created.
        pending_time (datetime, optional): The date and time the task was set to pending.
        prolog_time (datetime, optional): The date and time the task was set to prolog.
        running_time (datetime, optional): The date and time the task was set to running.
        finished_time (datetime, optional): The date and time the task was completed.
        eval_status (str, optional): Evaluation status.
        trial_number (int, optional): Which attempt to execute the process step this task represent.
        elapsed_time (float, optional): Number of seconds it took the evaluator to execute the task.
        task_definition_id (str): ('ID of the :class:`ansys.rep.client.jms.TaskDefinition` the task is linked to.',)
        task_definition_snapshot (optional): Snapshot of :class:`ansys.rep.client.jms.TaskDefinition` created when task status changes to prolog, before evaluation.
        job_id (str): ID of the :class:`ansys.rep.client.jms.Job` the task is linked to.
        evaluator_id (str, optional): UUID of the :class:`ansys.rep.client.jms.Evaluator` that updated the task.
        input_file_ids (list): List of IDs of input files of task.
        output_file_ids (list): List of IDs of output files of task.
        inherited_file_ids (list): List of IDs of inherited files of task.
        owned_file_ids (list): List of IDs of owned files of task.

    """

    class Meta:
        schema = TaskSchema
        rest_name = "tasks"

    def __init__(self, **kwargs):
        self.id = missing
        self.modification_time = missing
        self.creation_time = missing
        self.pending_time = missing
        self.prolog_time = missing
        self.running_time = missing
        self.finished_time = missing
        self.eval_status = missing
        self.trial_number = missing
        self.elapsed_time = missing
        self.task_definition_id = missing
        self.task_definition_snapshot = missing
        self.job_id = missing
        self.evaluator_id = missing
        self.input_file_ids = missing
        self.output_file_ids = missing
        self.inherited_file_ids = missing
        self.owned_file_ids = missing

        super().__init__(**kwargs)

TaskSchema.Meta.object_class = Task
