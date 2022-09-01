
from marshmallow.utils import missing
from .base import Object
from ..schema.evaluator import EvaluatorSchema

class Evaluator(Object):
    """Evaluator resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        host_id (str): Unique identifier built from hardware information and selected job_definition details of an evaluator.
        name (str, optional): Name of the evaluator.
        hostname (str, optional): Name of the host on which the evaluator is running.
        platform (str, optional): Operating system on which the evaluator is running.
        task_manager_type (str, optional): Type of the task manager used by the evaluator.
        project_server_select (bool, optional): Whether the evaluator allows server-driven assignment of projects or uses it's own local settings.
        alive_update_interval (int, optional): Minimal time (in seconds) between evaluator registration updates.
        update_time (datetime, optional): Last time the evaluator updated it's registration details. Used to check which evaluators are alive.
        external_access_port (int, optional): Port number for external access to the evaluator.
        project_assignment_mode (str, optional): Which strategy to use for selecting projects to work on.
        project_list (list): List of projects on which this evaluator should be working.
        configuration (dict, optional): Details of the evaluator configuration, including hardware info and available applications.

    """

    class Meta:
        schema = EvaluatorSchema
        rest_name = "evaluators"

    def __init__(self, **kwargs):
        self.id = missing
        self.host_id = missing
        self.name = missing
        self.hostname = missing
        self.platform = missing
        self.task_manager_type = missing
        self.project_server_select = missing
        self.alive_update_interval = missing
        self.update_time = missing
        self.external_access_port = missing
        self.project_assignment_mode = missing
        self.project_list = missing
        self.configuration = missing

        super().__init__(**kwargs)

EvaluatorSchema.Meta.object_class = Evaluator
