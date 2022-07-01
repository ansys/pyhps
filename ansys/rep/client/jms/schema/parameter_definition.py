# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from marshmallow import fields
from marshmallow_oneofschema import OneOfSchema

from .base import ObjectSchema

log = logging.getLogger(__name__)


class ParameterDefinitionBaseSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    name = fields.String(allow_none=True, description="Name (ID) of the parameter.")

    quantity_name = fields.String(
        allow_none=True, description="Name of the quantity the parameter represents, e.g. Length."
    )
    units = fields.String(allow_none=True, description="Units for the parameter.")
    display_text = fields.String(
        allow_none=True, description="Text to display as the parameter name."
    )

    mode = fields.String(
        load_only=True,
        description="Indicates whether it's an input or output parameter. Filled server side.",
    )


class FloatParameterDefinitionSchema(ParameterDefinitionBaseSchema):
    class Meta(ParameterDefinitionBaseSchema.Meta):
        pass

    type = fields.Constant("float")
    default = fields.Float(allow_none=True, description="Default parameter value.")
    lower_limit = fields.Float(allow_none=True, description="Lower bound for the parameter value.")
    upper_limit = fields.Float(allow_none=True, description="Upper bound for the parameter value.")
    step = fields.Float(
        allow_none=True,
        description="If provided, allowable values are given by: AllowableValue = lower_limit + n * step, where n is an integer and AllowableValue <= upper_limit.",
    )
    cyclic = fields.Bool(allow_none=True, description="Indicates if the parameter is cyclic.")
    value_list = fields.List(
        fields.Float(),
        allow_none=True,
        description="A list of allowed values, alternative to providing upper and lower limits.",
    )


class IntParameterDefinitionSchema(ParameterDefinitionBaseSchema):
    class Meta(ParameterDefinitionBaseSchema.Meta):
        pass

    type = fields.Constant("int")
    default = fields.Integer(allow_none=True, description="Default parameter value.")
    lower_limit = fields.Integer(
        allow_none=True, description="Lower bound for the parameter value."
    )
    upper_limit = fields.Integer(
        allow_none=True, description="Upper bound for the parameter value."
    )
    step = fields.Integer(allow_none=True, description="Equal to 1 by default.")
    cyclic = fields.Bool(allow_none=True, description="Indicates if the parameter is cyclic.")


class BoolParameterDefinitionSchema(ParameterDefinitionBaseSchema):
    class Meta(ParameterDefinitionBaseSchema.Meta):
        pass

    type = fields.Constant("bool")
    default = fields.Bool(allow_none=True, description="Default parameter value.")


class StringParameterDefinitionSchema(ParameterDefinitionBaseSchema):
    class Meta(ParameterDefinitionBaseSchema.Meta):
        pass

    type = fields.Constant("string")
    default = fields.String(allow_none=True, description="Default parameter value.")
    value_list = fields.List(
        fields.String(), allow_none=True, description="A list of allowed values."
    )


class ParameterDefinitionSchema(OneOfSchema):
    type_field = "type"

    type_schemas = {
        "float": FloatParameterDefinitionSchema,
        "int": IntParameterDefinitionSchema,
        "bool": BoolParameterDefinitionSchema,
        "string": StringParameterDefinitionSchema,
    }

    def get_obj_type(self, obj):
        return obj.__class__.__name__.replace("ParameterDefinition", "").lower()
