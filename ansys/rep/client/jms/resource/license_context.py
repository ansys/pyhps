# autogenerated code
from marshmallow.utils import missing
from ansys.rep.client.common import Object
from ..schema.license_context import LicenseContextSchema

class LicenseContext(Object):
    """LicenseContext resource.

    Parameters
    ----------
    context_id : str, optional
        License context ID
    environment : dict, optional
        License context environment dict

    """

    class Meta:
        schema = LicenseContextSchema
        rest_name = "license_contexts"

    def __init__(self,
        context_id=missing,
        environment=missing,
        **kwargs
    ):
        self.context_id = context_id
        self.environment = environment

        self.obj_type = self.__class__.__name__

LicenseContextSchema.Meta.object_class = LicenseContext
