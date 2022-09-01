
from marshmallow.utils import missing
from .base import Object
from ..schema.parameter_definition import ParameterDefinitionSchema

class ParameterDefinition(Object):
    """ParameterDefinition resource.

    Parameters:

    """

    class Meta:
        schema = ParameterDefinitionSchema
        rest_name = "parameter_definitions"

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

ParameterDefinitionSchema.Meta.object_class = ParameterDefinition
