
from marshmallow.utils import missing
from .parameter_definition import ParameterDefinition
from ..schema.parameter_definition import StringParameterDefinitionSchema

class StringParameterDefinition(ParameterDefinition):
    """StringParameterDefinition resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        name (str, optional): Name (ID) of the parameter.
        quantity_name (str, optional): Name of the quantity the parameter represents, e.g. Length.
        units (str, optional): Units for the parameter.
        display_text (str, optional): Text to display as the parameter name.
        mode (str): Indicates whether it's an input or output parameter. Filled server side.
        type
        default (str, optional): Default parameter value.
        value_list (list, optional): A list of allowed values.

    """

    class Meta:
        schema = StringParameterDefinitionSchema
        rest_name = "parameter_definitions"

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.quantity_name = missing
        self.units = missing
        self.display_text = missing
        self.mode = missing
        self.type = missing
        self.default = missing
        self.value_list = missing

        super().__init__(**kwargs)

StringParameterDefinitionSchema.Meta.object_class = StringParameterDefinition
