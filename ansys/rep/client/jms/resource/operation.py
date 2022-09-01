
from marshmallow.utils import missing
from .base import Object
from ..schema.operation import OperationSchema

class Operation(Object):
    """Operation resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        name (str, optional)
        finished (bool, optional)
        succeeded (bool, optional)
        progress (float, optional)
        status (str, optional)
        result (dict, optional)
        messages (list, optional)
        start_time (datetime, optional)
        end_time (datetime, optional)

    """

    class Meta:
        schema = OperationSchema
        rest_name = "operations"

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.finished = missing
        self.succeeded = missing
        self.progress = missing
        self.status = missing
        self.result = missing
        self.messages = missing
        self.start_time = missing
        self.end_time = missing

        super().__init__(**kwargs)

OperationSchema.Meta.object_class = Operation
