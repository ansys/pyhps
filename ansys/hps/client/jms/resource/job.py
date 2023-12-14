# autogenerated code
from marshmallow.utils import missing
from ansys.hps.client.common import Object
from ..schema.job import JobSchema

class Job(Object):
    """Job resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    creation_time : datetime, optional
        The date and time the resource was created.
    modification_time : datetime, optional
        The date and time the resource was last modified.
    created_by : str, optional
        ID of the user who created the object.
    modified_by : str, optional
        ID of the user who last modified the object.
    name : str, optional
        Name of the job.
    eval_status : str
        Evaluation status.
    job_definition_id : str
        ID of the linked job definition, see :class:`JobDefinition`.
    priority : int, optional
        Priority with which jobs are evaluated. The default is 0, which is the highest priority. Assigning a higher value to a design point makes it a lower priority.
    values : dict[str, any], optional
        Dictionary with (name,value) pairs for all parameters defined in the linked job definition.
    fitness : float, optional
        Fitness value computed.
    fitness_term_values : dict[str, float], optional
        Dictionary with (name,value) pairs for all fitness terms computed.
    note : str, optional
        Optional note for this job.
    creator : str, optional
        Optional name/ID of the creator of this job.
    executed_level : int, optional
        Execution level of the last executed task (-1 if none has been executed yet).
    elapsed_time : float
        Number of seconds it took the evaluator(s) to update the job.
    host_ids : list, optional
        List of Host IDs of the evaluators that updated the job.
    file_ids : list[str]
        List of IDs of all files of this job.

    """

    class Meta:
        schema = JobSchema
        rest_name = "jobs"

    def __init__(self,
        id=missing,
        creation_time=missing,
        modification_time=missing,
        created_by=missing,
        modified_by=missing,
        name=missing,
        eval_status=missing,
        job_definition_id=missing,
        priority=missing,
        values=missing,
        fitness=missing,
        fitness_term_values=missing,
        note=missing,
        creator=missing,
        executed_level=missing,
        elapsed_time=missing,
        host_ids=missing,
        file_ids=missing,
        **kwargs
    ):
        self.id = id
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.name = name
        self.eval_status = eval_status
        self.job_definition_id = job_definition_id
        self.priority = priority
        self.values = values
        self.fitness = fitness
        self.fitness_term_values = fitness_term_values
        self.note = note
        self.creator = creator
        self.executed_level = executed_level
        self.elapsed_time = elapsed_time
        self.host_ids = host_ids
        self.file_ids = file_ids

        self.obj_type = self.__class__.__name__

JobSchema.Meta.object_class = Job
