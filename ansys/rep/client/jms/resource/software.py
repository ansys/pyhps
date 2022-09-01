
from marshmallow.utils import missing
from .base import Object
from ..schema.task_definition import SoftwareSchema

class Software(Object):
    """Software resource.

    Parameters:
        name (str): Application's name.
        version (str, optional): Application's version.

    """

    class Meta:
        schema = SoftwareSchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.name = missing
        self.version = missing

        super().__init__(**kwargs)

SoftwareSchema.Meta.object_class = Software
