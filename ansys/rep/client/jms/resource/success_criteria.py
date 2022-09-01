
from marshmallow.utils import missing
from .base import Object
from ..schema.task_definition import SuccessCriteriaSchema

class SuccessCriteria(Object):
    """SuccessCriteria resource.

    Parameters:
        return_code (int, optional): The process exit code that must be returned by the executed command.
        expressions (list, optional): A list of expressions to be evaluated.
        required_output_file_ids (list, optional): List of IDs of required output files.
        require_all_output_files (bool, optional): Flag to require all output files.
        required_output_parameter_ids (list, optional): List of names of required output parameters.
        require_all_output_parameters (bool, optional): Flag to require all output parameters.

    """

    class Meta:
        schema = SuccessCriteriaSchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.return_code = missing
        self.expressions = missing
        self.required_output_file_ids = missing
        self.require_all_output_files = missing
        self.required_output_parameter_ids = missing
        self.require_all_output_parameters = missing

        super().__init__(**kwargs)

SuccessCriteriaSchema.Meta.object_class = SuccessCriteria
