
from marshmallow.utils import missing
from .base import Object
from ..schema.task_definition import ResourceRequirementsSchema

class ResourceRequirements(Object):
    """ResourceRequirements resource.

    Parameters:
        platform (str, optional)
        memory (int, optional)
        cpu_core_usage (float, optional)
        disk_space (int, optional)
        custom (dict, optional)

    """

    class Meta:
        schema = ResourceRequirementsSchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.platform = missing
        self.memory = missing
        self.cpu_core_usage = missing
        self.disk_space = missing
        self.custom = missing

        super().__init__(**kwargs)

ResourceRequirementsSchema.Meta.object_class = ResourceRequirements
