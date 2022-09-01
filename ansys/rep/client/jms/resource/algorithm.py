
from marshmallow.utils import missing
from .base import Object
from ..schema.algorithm import AlgorithmSchema

class Algorithm(Object):
    """Algorithm resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        name (str, optional): Name of the algorithm.
        description (str, optional): Description of the algorithm.
        creation_time (datetime, optional): The date and time the algorithm was created.
        modification_time (datetime, optional): The date and time the algorithm was last modified.
        data (str, optional): Generic string field to hold arbitrary algorithm job_definition data, e.g. as JSON dictionary.
        jobs (list): List of design point IDs.

    """

    class Meta:
        schema = AlgorithmSchema
        rest_name = "algorithms"

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.description = missing
        self.creation_time = missing
        self.modification_time = missing
        self.data = missing
        self.jobs = missing

        super().__init__(**kwargs)

AlgorithmSchema.Meta.object_class = Algorithm
