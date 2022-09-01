
from marshmallow.utils import missing
from .base import Object
from ..schema.task_definition import LicensingSchema

class Licensing(Object):
    """Licensing resource.

    Parameters:
        enable_shared_licensing (bool, optional): Whether to enable shared licensing contexts for Ansys simulations

    """

    class Meta:
        schema = LicensingSchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.enable_shared_licensing = missing

        super().__init__(**kwargs)

LicensingSchema.Meta.object_class = Licensing
