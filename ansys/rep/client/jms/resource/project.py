# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from cachetools import TTLCache, cached
from marshmallow.utils import missing
import requests

from ansys.rep.client.exceptions import REPError

from ..schema.project import ProjectSchema
from .base import Object

log = logging.getLogger(__name__)


class Project(Object):
    """Project resource

    Args:
        **kwargs: Arbitrary keyword arguments, see the Project schema below.

    Example:

        >>> proj = Project(id="demo_project", active=True, priority=10)
        >>> proj = client.create_project(proj, replace=True)

    The Project schema has the following fields:

    .. jsonschema:: schemas/Project.json

    """

    class Meta:
        schema = ProjectSchema

    def __init__(self, **kwargs):
        super(Project, self).__init__(**kwargs)


ProjectSchema.Meta.object_class = Project


@cached(cache=TTLCache(1024, 60), key=lambda project: project.id)
def get_fs_url(project: Project):
    if project.file_storages == missing:
        raise REPError(f"The project object has no file storages information.")
    rest_gateways = [fs for fs in project.file_storages if fs["obj_type"] == "RestGateway"]
    rest_gateways.sort(key=lambda fs: fs["priority"], reverse=True)

    if not rest_gateways:
        raise REPError(
            f"Project {project.display_name} (id={project.id}) has no Rest Gateway defined."
        )

    for d in rest_gateways:
        url = d["url"]
        try:
            r = requests.get(url, verify=False, timeout=2)
        except Exception as ex:
            log.debug(ex)
            continue
        if r.status_code == 200:
            return url
    return None
