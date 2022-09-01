
from marshmallow.utils import missing
from .base import Object
from ..schema.job_definition import JobDefinitionSchema

class JobDefinition(Object):
    """JobDefinition resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        name (str, optional): Name of the job_definition
        active (bool): Defines whether this is the active job_definition in the project where evaluators will evaluate pending design points
        creation_time (datetime, optional): The date and time the job_definition was created.
        modification_time (datetime, optional): The date and time the job_definition was last modified.
        parameter_definition_ids (list)
        parameter_mapping_ids (list)
        task_definition_ids (list)
        fitness_definition (optional): An :class:`ansys.rep.client.jms.FitnessDefinition` object.

    """

    class Meta:
        schema = JobDefinitionSchema
        rest_name = "job_definitions"

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.active = missing
        self.creation_time = missing
        self.modification_time = missing
        self.parameter_definition_ids = missing
        self.parameter_mapping_ids = missing
        self.task_definition_ids = missing
        self.fitness_definition = missing

        super().__init__(**kwargs)

JobDefinitionSchema.Meta.object_class = JobDefinition
