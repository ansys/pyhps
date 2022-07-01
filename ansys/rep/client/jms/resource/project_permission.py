# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import json
import logging

from ..schema.project_permission import ProjectPermissionSchema
from .base import Object

log = logging.getLogger(__name__)


class ProjectPermission(Object):
    class Meta:
        schema = ProjectPermissionSchema
        rest_name = "permissions"

    def __init__(self, project=None, **kwargs):
        self.project = project
        super(ProjectPermission, self).__init__(**kwargs)


ProjectPermissionSchema.Meta.object_class = ProjectPermission


def update_permissions(project, permissions):

    if not permissions:
        return

    url = f"{project.client.jms_api_url}/projects/{project.id}/permissions"

    schema = ProjectPermissionSchema(many=True)
    serialized_data = schema.dump(permissions)
    json_data = json.dumps({"permissions": serialized_data})
    r = project.client.session.put(f"{url}", data=json_data)
