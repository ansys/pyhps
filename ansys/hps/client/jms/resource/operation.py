# autogenerated code
from marshmallow.utils import missing
from ansys.hps.client.common import Object
from ..schema.operation import OperationSchema

class Operation(Object):
    """Operation resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    name : str, optional
    target : list, optional
    finished : bool, optional
    succeeded : bool, optional
    progress : float, optional
    status : str, optional
    result : dict, optional
    messages : list, optional
    start_time : datetime, optional
    end_time : datetime, optional

    """

    class Meta:
        schema = OperationSchema
        rest_name = "operations"

    def __init__(self,
        id=missing,
        name=missing,
        target=missing,
        finished=missing,
        succeeded=missing,
        progress=missing,
        status=missing,
        result=missing,
        messages=missing,
        start_time=missing,
        end_time=missing,
        **kwargs
    ):
        self.id = id
        self.name = name
        self.target = target
        self.finished = finished
        self.succeeded = succeeded
        self.progress = progress
        self.status = status
        self.result = result
        self.messages = messages
        self.start_time = start_time
        self.end_time = end_time

        self.obj_type = self.__class__.__name__

OperationSchema.Meta.object_class = Operation
