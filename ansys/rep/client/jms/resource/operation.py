import logging

from ..schema.operation import OperationSchema
from .base import Object

log = logging.getLogger(__name__)


class Operation(Object):
    """Operation resource.

    The operation schema has the following fields:

    .. jsonschema:: schemas/Operation.json

    """

    class Meta:
        schema = OperationSchema
        rest_name = "operations"

    def __init__(self, **kwargs):
        super(Operation, self).__init__(**kwargs)


OperationSchema.Meta.object_class = Operation
