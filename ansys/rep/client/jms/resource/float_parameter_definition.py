
from marshmallow.utils import missing
from .parameter_definition import ParameterDefinition
from ..schema.parameter_definition import FloatParameterDefinitionSchema

class FloatParameterDefinition(ParameterDefinition):
    """FloatParameterDefinition resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        name (str, optional): Name (ID) of the parameter.
        quantity_name (str, optional): Name of the quantity the parameter represents, e.g. Length.
        units (str, optional): Units for the parameter.
        display_text (str, optional): Text to display as the parameter name.
        mode (str): Indicates whether it's an input or output parameter. Filled server side.
        type
        default (float, optional): Default parameter value.
        lower_limit (float, optional): Lower bound for the parameter value.
        upper_limit (float, optional): Upper bound for the parameter value.
        step (float, optional): If provided, allowable values are given by: AllowableValue = lower_limit + n * step, where n is an integer and AllowableValue <= upper_limit.
        cyclic (bool, optional): Indicates if the parameter is cyclic.
        value_list (list, optional): A list of allowed values, alternative to providing upper and lower limits.

    """

    class Meta:
        schema = FloatParameterDefinitionSchema
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
        self.lower_limit = missing
        self.upper_limit = missing
        self.step = missing
        self.cyclic = missing
        self.value_list = missing

        super().__init__(**kwargs)

FloatParameterDefinitionSchema.Meta.object_class = FloatParameterDefinition
