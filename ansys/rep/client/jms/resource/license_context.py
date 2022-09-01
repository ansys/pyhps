
from marshmallow.utils import missing
from .base import Object
from ..schema.license_context import LicenseContextSchema

class LicenseContext(Object):
    """LicenseContext resource.

    Parameters:
        context_id (str, optional): License context ID
        environment (dict, optional): License context environment dict

    """

    class Meta:
        schema = LicenseContextSchema
        rest_name = "license_contexts"

    def __init__(self, **kwargs):
        self.context_id = missing
        self.environment = missing

        super().__init__(**kwargs)

LicenseContextSchema.Meta.object_class = LicenseContext
