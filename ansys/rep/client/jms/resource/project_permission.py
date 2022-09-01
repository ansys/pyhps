# autogenerated on 2022-09-01 17:37 based on ProjectPermissionSchema

from marshmallow.utils import missing
from .base import Object
from ..schema.project_permission import ProjectPermissionSchema

class ProjectPermission(Object):
    """ProjectPermission resource.

    Parameters:
        permission_type (str)
        value_id (str)
        value_name (str, optional)
        role (str)

    """

    class Meta:
        schema = ProjectPermissionSchema
        rest_name = "permissions"

    def __init__(self, **kwargs):
        self.permission_type = missing
        self.value_id = missing
        self.value_name = missing
        self.role = missing

        super().__init__(**kwargs)

ProjectPermissionSchema.Meta.object_class = ProjectPermission
