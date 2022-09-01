
from marshmallow.utils import missing
from .base import Object
from ..schema.selection import JobSelectionSchema

class JobSelection(Object):
    """JobSelection resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        name (str): Name of the selection.
        creation_time (datetime, optional): The date and time the selection was created.
        modification_time (datetime, optional): The date and time the selection was last modified.
        algorithm_id (str, optional): ID of the :class:`ansys.rep.client.jms.Algorithm` the selection belongs to (optional).
        jobs (list): List of design point IDs.

    """

    class Meta:
        schema = JobSelectionSchema
        rest_name = "job_selections"

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.creation_time = missing
        self.modification_time = missing
        self.algorithm_id = missing
        self.jobs = missing

        super().__init__(**kwargs)

JobSelectionSchema.Meta.object_class = JobSelection
