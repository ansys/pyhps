# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module providing float, integer, boolean, and string parameter definition schema."""

import logging

from marshmallow import fields
from marshmallow_oneofschema import OneOfSchema

from ansys.hps.client.common import ObjectSchemaWithModificationInfo

log = logging.getLogger(__name__)


class ParameterDefinitionBaseSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(allow_none=True, metadata={"description": "Name (ID) of the parameter."})

    quantity_name = fields.String(
        allow_none=True,
        metadata={
            "description": "Name of the quantity that the parameter represents. "
            "For example, ``Length``."
        },
    )
    units = fields.String(allow_none=True, metadata={"description": "Units for the parameter."})
    display_text = fields.String(
        allow_none=True, metadata={"description": "Text to display as the parameter name."}
    )

    mode = fields.String(
        load_only=True,
        metadata={
            "description": "Indicates whether it's an input "
            "or output parameter. The mode is filled server-side."
        },
    )


class FloatParameterDefinitionSchema(ParameterDefinitionBaseSchema):
    class Meta(ParameterDefinitionBaseSchema.Meta):
        pass

    type = fields.Constant("float")
    default = fields.Float(allow_none=True, metadata={"description": "Default parameter value."})
    lower_limit = fields.Float(
        allow_none=True, metadata={"description": "Lower bound for the parameter value."}
    )
    upper_limit = fields.Float(
        allow_none=True, metadata={"description": "Upper bound for the parameter value."}
    )
    step = fields.Float(
        allow_none=True,
        metadata={
            "description": "If provided, allowable values are given by: "
            "AllowableValue = lower_limit + n * step, "
            "where n is an integer and AllowableValue <= upper_limit."
        },
    )
    cyclic = fields.Bool(
        allow_none=True, metadata={"description": "Whether the parameter is cyclic."}
    )
    value_list = fields.List(
        fields.Float(),
        allow_none=True,
        metadata={
            "description": "List of allowed values. This parameter provides an alternative "
            "to specifying upper and lower limits."
        },
    )


class IntParameterDefinitionSchema(ParameterDefinitionBaseSchema):
    class Meta(ParameterDefinitionBaseSchema.Meta):
        pass

    type = fields.Constant("int")
    default = fields.Integer(allow_none=True, metadata={"description": "Default parameter value."})
    lower_limit = fields.Integer(
        allow_none=True, metadata={"description": "Lower bound for the parameter value."}
    )
    upper_limit = fields.Integer(
        allow_none=True, metadata={"description": "Upper bound for the parameter value."}
    )
    step = fields.Integer(allow_none=True, metadata={"description": "The default is ``1``."})
    cyclic = fields.Bool(
        allow_none=True, metadata={"description": "Whether the parameter is cyclic."}
    )


class BoolParameterDefinitionSchema(ParameterDefinitionBaseSchema):
    class Meta(ParameterDefinitionBaseSchema.Meta):
        pass

    type = fields.Constant("bool")
    default = fields.Bool(allow_none=True, metadata={"description": "Default parameter value."})


class StringParameterDefinitionSchema(ParameterDefinitionBaseSchema):
    class Meta(ParameterDefinitionBaseSchema.Meta):
        pass

    type = fields.Constant("string")
    default = fields.String(allow_none=True, metadata={"description": "Default parameter value."})
    value_list = fields.List(
        fields.String(), allow_none=True, metadata={"description": "List of allowed values."}
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
        """Return the type of parameter definition."""
        return obj.__class__.__name__.replace("ParameterDefinition", "").lower()
