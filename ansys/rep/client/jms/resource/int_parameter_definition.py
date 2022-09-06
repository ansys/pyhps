# autogenerated code based on IntParameterDefinitionSchema

from marshmallow.utils import missing
from .parameter_definition import ParameterDefinition
from ..schema.parameter_definition import IntParameterDefinitionSchema

class IntParameterDefinition(ParameterDefinition):
    """IntParameterDefinition resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    name : str, optional
        Name (ID) of the parameter.
    quantity_name : str, optional
        Name of the quantity the parameter represents, e.g. Length.
    units : str, optional
        Units for the parameter.
    display_text : str, optional
        Text to display as the parameter name.
    mode : str
        Indicates whether it's an input or output parameter. Filled server side.
    type : str
    default : int, optional
        Default parameter value.
    lower_limit : int, optional
        Lower bound for the parameter value.
    upper_limit : int, optional
        Upper bound for the parameter value.
    step : int, optional
        Equal to 1 by default.
    cyclic : bool, optional
        Indicates if the parameter is cyclic.

    """

    class Meta:
        schema = IntParameterDefinitionSchema
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

        super().__init__(**kwargs)

IntParameterDefinitionSchema.Meta.object_class = IntParameterDefinition
