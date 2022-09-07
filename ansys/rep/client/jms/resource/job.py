# autogenerated code based on JobSchema

from marshmallow.utils import missing
from ansys.rep.client.common import Object
from ..schema.job import JobSchema

class Job(Object):
    """Job resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    name : str, optional
        Name of the job.
    eval_status : str
        Evaluation status.
    job_definition_id : str
        ID of the linked job definition, see :class:`JobDefinition`.
    priority : int, optional
        Priority with which jobs are evaluated. The default is 0, which is the highest priority. Assigning a higher value to a design point makes it a lower priority.
    values : dict, optional
        Dictionary with (name,value) pairs for all parameters defined in the linked job definition.
    fitness : float, optional
        Fitness value computed.
    fitness_term_values : dict, optional
        Dictionary with (name,value) pairs for all fitness terms computed.
    note : str, optional
        Optional note for this job.
    creator : str, optional
        Optional name/ID of the creator of this job.
    executed_task_definition_level : int, optional
        Execution level of the last executed process step (-1 if none has been executed yet).
    creation_time : datetime, optional
        The date and time the job was created.
    modification_time : datetime, optional
        The date and time the job was last modified.
    elapsed_time : float
        Number of seconds it took the evaluator(s) to update the job.
    evaluators : list, optional
        List of IDs of the evaluators that updated the job.
    file_ids : list[str]
        List of IDs of all files of this job.

    """

    class Meta:
        schema = JobSchema
        rest_name = "jobs"

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.eval_status = missing
        self.job_definition_id = missing
        self.priority = missing
        self.values = missing
        self.fitness = missing
        self.fitness_term_values = missing
        self.note = missing
        self.creator = missing
        self.executed_task_definition_level = missing
        self.creation_time = missing
        self.modification_time = missing
        self.elapsed_time = missing
        self.evaluators = missing
        self.file_ids = missing

        super().__init__(**kwargs)

JobSchema.Meta.object_class = Job
