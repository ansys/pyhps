# autogenerated code
from marshmallow.utils import missing
from ansys.rep.client.common import Object
from ..schema.parameter_definition import ParameterDefinitionSchema
from ..schema.parameter_definition import FloatParameterDefinitionSchema
from ..schema.parameter_definition import IntParameterDefinitionSchema
from ..schema.parameter_definition import BoolParameterDefinitionSchema
from ..schema.parameter_definition import StringParameterDefinitionSchema

class ParameterDefinition(Object):
    """ParameterDefinition resource.

    Parameters
    ----------

    """

    class Meta:
        schema = ParameterDefinitionSchema
        rest_name = "parameter_definitions"

    def __init__(self,

    ):

        self.obj_type = self.__class__.__name__

ParameterDefinitionSchema.Meta.object_class = ParameterDefinition

class FloatParameterDefinition(ParameterDefinition):
    """FloatParameterDefinition resource.

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
    default : float, optional
        Default parameter value.
    lower_limit : float, optional
        Lower bound for the parameter value.
    upper_limit : float, optional
        Upper bound for the parameter value.
    step : float, optional
        If provided, allowable values are given by: AllowableValue = lower_limit + n * step, where n is an integer and AllowableValue <= upper_limit.
    cyclic : bool, optional
        Indicates if the parameter is cyclic.
    value_list : list, optional
        A list of allowed values, alternative to providing upper and lower limits.

    """

    class Meta:
        schema = FloatParameterDefinitionSchema
        rest_name = "parameter_definitions"

    def __init__(self,
        id=missing,
        name=missing,
        quantity_name=missing,
        units=missing,
        display_text=missing,
        mode=missing,
        type=missing,
        default=missing,
        lower_limit=missing,
        upper_limit=missing,
        step=missing,
        cyclic=missing,
        value_list=missing
    ):
        self.id = id
        self.name = name
        self.quantity_name = quantity_name
        self.units = units
        self.display_text = display_text
        self.mode = mode
        self.type = type
        self.default = default
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.step = step
        self.cyclic = cyclic
        self.value_list = value_list

        self.obj_type = self.__class__.__name__

FloatParameterDefinitionSchema.Meta.object_class = FloatParameterDefinition

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

    def __init__(self,
        id=missing,
        name=missing,
        quantity_name=missing,
        units=missing,
        display_text=missing,
        mode=missing,
        type=missing,
        default=missing,
        lower_limit=missing,
        upper_limit=missing,
        step=missing,
        cyclic=missing
    ):
        self.id = id
        self.name = name
        self.quantity_name = quantity_name
        self.units = units
        self.display_text = display_text
        self.mode = mode
        self.type = type
        self.default = default
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.step = step
        self.cyclic = cyclic

        self.obj_type = self.__class__.__name__

IntParameterDefinitionSchema.Meta.object_class = IntParameterDefinition

class BoolParameterDefinition(ParameterDefinition):
    """BoolParameterDefinition resource.

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
    default : bool, optional
        Default parameter value.

    """

    class Meta:
        schema = BoolParameterDefinitionSchema
        rest_name = "parameter_definitions"

    def __init__(self,
        id=missing,
        name=missing,
        quantity_name=missing,
        units=missing,
        display_text=missing,
        mode=missing,
        type=missing,
        default=missing
    ):
        self.id = id
        self.name = name
        self.quantity_name = quantity_name
        self.units = units
        self.display_text = display_text
        self.mode = mode
        self.type = type
        self.default = default

        self.obj_type = self.__class__.__name__

BoolParameterDefinitionSchema.Meta.object_class = BoolParameterDefinition

class StringParameterDefinition(ParameterDefinition):
    """StringParameterDefinition resource.

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
    default : str, optional
        Default parameter value.
    value_list : list, optional
        A list of allowed values.

    """

    class Meta:
        schema = StringParameterDefinitionSchema
        rest_name = "parameter_definitions"

    def __init__(self,
        id=missing,
        name=missing,
        quantity_name=missing,
        units=missing,
        display_text=missing,
        mode=missing,
        type=missing,
        default=missing,
        value_list=missing
    ):
        self.id = id
        self.name = name
        self.quantity_name = quantity_name
        self.units = units
        self.display_text = display_text
        self.mode = mode
        self.type = type
        self.default = default
        self.value_list = value_list

        self.obj_type = self.__class__.__name__

StringParameterDefinitionSchema.Meta.object_class = StringParameterDefinition
