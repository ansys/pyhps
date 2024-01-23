# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

# autogenerated code
from marshmallow.utils import missing

from ansys.hps.client.common import Object

from ..schema.parameter_mapping import ParameterMappingSchema


class ParameterMapping(Object):
    """Provides the parameter mapping resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    creation_time : datetime, optional
        Date and time that the resource was created.
    modification_time : datetime, optional
        Date and time that the resource was last modified.
    created_by : str, optional
        ID of the user who created the object.
    modified_by : str, optional
        ID of the user who last modified the object.
    line : int, optional
    column : int, optional
    key_string : str, optional
    float_field : str, optional
    width : int, optional
    precision : int, optional
    tokenizer : str, optional
    decimal_symbol : str, optional
    digit_grouping_symbol : str, optional
    string_quote : str, optional
    true_string : str, optional
    false_string : str, optional
    parameter_definition_id : str, optional
        ID of the linked parameter definition. For more information, see the
        :class:`ParameterDefinition` class.
    task_definition_property : str, optional
    file_id : str, optional
        ID of the file resource.
    """

    class Meta:
        schema = ParameterMappingSchema
        rest_name = "parameter_mappings"

    def __init__(
        self,
        id=missing,
        creation_time=missing,
        modification_time=missing,
        created_by=missing,
        modified_by=missing,
        line=missing,
        column=missing,
        key_string=missing,
        float_field=missing,
        width=missing,
        precision=missing,
        tokenizer=missing,
        decimal_symbol=missing,
        digit_grouping_symbol=missing,
        string_quote=missing,
        true_string=missing,
        false_string=missing,
        parameter_definition_id=missing,
        task_definition_property=missing,
        file_id=missing,
        **kwargs
    ):
        self.id = id
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.line = line
        self.column = column
        self.key_string = key_string
        self.float_field = float_field
        self.width = width
        self.precision = precision
        self.tokenizer = tokenizer
        self.decimal_symbol = decimal_symbol
        self.digit_grouping_symbol = digit_grouping_symbol
        self.string_quote = string_quote
        self.true_string = true_string
        self.false_string = false_string
        self.parameter_definition_id = parameter_definition_id
        self.task_definition_property = task_definition_property
        self.file_id = file_id

        self.obj_type = self.__class__.__name__


ParameterMappingSchema.Meta.object_class = ParameterMapping
