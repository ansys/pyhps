
from marshmallow.utils import missing
from .base import Object
from ..schema.parameter_mapping import ParameterMappingSchema

class ParameterMapping(Object):
    """ParameterMapping resource.

    Parameters:
        id (str, optional): Unique ID to access the resource, generated internally by the server on creation.
        line (int, optional)
        column (int, optional)
        key_string (str, optional)
        float_field (str, optional)
        width (int, optional)
        precision (int, optional)
        tokenizer (str, optional)
        decimal_symbol (str, optional)
        digit_grouping_symbol (str, optional)
        string_quote (str, optional)
        true_string (str, optional)
        false_string (str, optional)
        parameter_definition_id (str, optional): ID of the linked parameter definition, see :class:`ansys.rep.client.jms.ParameterDefinition`.
        task_definition_property (str, optional)
        file_id (str, optional): ID of the file resource.

    """

    class Meta:
        schema = ParameterMappingSchema
        rest_name = "parameter_mappings"

    def __init__(self, **kwargs):
        self.id = missing
        self.line = missing
        self.column = missing
        self.key_string = missing
        self.float_field = missing
        self.width = missing
        self.precision = missing
        self.tokenizer = missing
        self.decimal_symbol = missing
        self.digit_grouping_symbol = missing
        self.string_quote = missing
        self.true_string = missing
        self.false_string = missing
        self.parameter_definition_id = missing
        self.task_definition_property = missing
        self.file_id = missing

        super().__init__(**kwargs)

ParameterMappingSchema.Meta.object_class = ParameterMapping
