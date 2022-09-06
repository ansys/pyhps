# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from marshmallow import fields

from .base import ObjectSchema
from .object_reference import IdReference

log = logging.getLogger(__name__)


class ParameterMappingSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    line = fields.Int(allow_none=True)
    column = fields.Int(allow_none=True)
    key_string = fields.String(allow_none=True)
    float_field = fields.String(allow_none=True)
    width = fields.Int(allow_none=True)
    precision = fields.Int(allow_none=True)
    tokenizer = fields.String(allow_none=True, description="")
    decimal_symbol = fields.String(allow_none=True)
    digit_grouping_symbol = fields.String(allow_none=True)
    string_quote = fields.String(allow_none=True)
    true_string = fields.String(allow_none=True)
    false_string = fields.String(allow_none=True)
    parameter_definition_id = IdReference(
        allow_none=True,
        attribute="parameter_definition_id",
        referenced_class="ParameterDefinition",
        description="ID of the linked parameter definition, " "see :class:`ParameterDefinition`.",
    )
    task_definition_property = fields.String(allow_none=True)
    file_id = IdReference(
        allow_none=True,
        attribute="file_id",
        referenced_class="File",
        description="ID of the file resource.",
    )
