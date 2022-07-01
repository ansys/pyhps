# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.parameter_definition import (
    BoolParameterDefinitionSchema,
    FloatParameterDefinitionSchema,
    IntParameterDefinitionSchema,
    ParameterDefinitionSchema,
    StringParameterDefinitionSchema,
)
from .base import Object

log = logging.getLogger(__name__)


class ParameterDefinition(Object):
    class Meta:
        schema = ParameterDefinitionSchema
        rest_name = "parameter_definitions"

    def __init__(self, **kwargs):
        super(ParameterDefinition, self).__init__(**kwargs)


ParameterDefinitionSchema.Meta.object_class = ParameterDefinition


class FloatParameterDefinition(ParameterDefinition):
    """FloatParameterDefinition resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the FloatParameterDefinition schema below.

    Example:

        >>> # A continuos parameter
        >>> pd1 = FloatParameterDefinition(name='param_1', lower_limit=4.0, upper_limit=20.0, default=12.0 )
        >>> # In case of e.g. a manifacturing variable which can only take some values
        >>> pd2 = FloatParameterDefinition(name='param_2', value_list=[4.7, 12.0, 15.5, 20.0], default=12.0)

    The FloatParameterDefinition schema has the following fields:

    .. jsonschema:: schemas/FloatParameterDefinition.json

    """

    class Meta(ParameterDefinition.Meta):
        schema = FloatParameterDefinitionSchema

    def __init__(self, **kwargs):
        super(FloatParameterDefinition, self).__init__(**kwargs)


FloatParameterDefinitionSchema.Meta.object_class = FloatParameterDefinition


class IntParameterDefinition(ParameterDefinition):
    """IntParameterDefinition resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the IntParameterDefinition schema below.

    Example:

        >>> pd1 = IntParameterDefinition(name='ply_angle', value_list=[-60, -45, 0, 45, 60], default=0)
        >>> pd2 = IntParameterDefinition(name='number_of_layers', lower_limit=1, upper_limit=5, default=2, step=1)

    The IntParameterDefinition schema has the following fields:

    .. jsonschema:: schemas/IntParameterDefinition.json

    """

    class Meta(ParameterDefinition.Meta):
        schema = IntParameterDefinitionSchema

    def __init__(self, **kwargs):
        super(IntParameterDefinition, self).__init__(**kwargs)


IntParameterDefinitionSchema.Meta.object_class = IntParameterDefinition


class BoolParameterDefinition(ParameterDefinition):
    """BoolParameterDefinition resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the BoolParameterDefinition schema below.

    The BoolParameterDefinition schema has the following fields:

    .. jsonschema:: schemas/BoolParameterDefinition.json

    """

    class Meta(ParameterDefinition.Meta):
        schema = BoolParameterDefinitionSchema

    def __init__(self, **kwargs):
        super(BoolParameterDefinition, self).__init__(**kwargs)


BoolParameterDefinitionSchema.Meta.object_class = BoolParameterDefinition


class StringParameterDefinition(ParameterDefinition):
    """StringParameterDefinition resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the StringParameterDefinition schema below.

    Example:

        >>> pd = StringParameterDefinition(name='DiameterDistribution', value_list=['Constant', 'Uniform', 'Log-Normal'], default='Constant')

    The StringParameterDefinition schema has the following fields:

    .. jsonschema:: schemas/StringParameterDefinition.json

    """

    class Meta(ParameterDefinition.Meta):
        schema = StringParameterDefinitionSchema

    def __init__(self, **kwargs):
        super(StringParameterDefinition, self).__init__(**kwargs)


StringParameterDefinitionSchema.Meta.object_class = StringParameterDefinition
