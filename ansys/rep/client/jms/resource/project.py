# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import json
import logging
import os
import time
import uuid

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
        client (:class:`ansys.rep.client.jms.Client`, optional): A client object. Defaults to None.
        **kwargs: Arbitrary keyword arguments, see the Project schema below.

    Example:

        >>> proj = Project(id="demo_project", active=True, priority=10)
        >>> proj = client.create_project(proj, replace=True)

    The Project schema has the following fields:

    .. jsonschema:: schemas/Project.json

    """

    class Meta:
        schema = ProjectSchema

    def __init__(self, client=None, **kwargs):
        self.client = client
        super(Project, self).__init__(**kwargs)

    ################################################################
    # Others
    def copy(self, project_name):
        """Create a copy of the project

        Args:
            project_id (str): ID of the new project.
        """
        return copy_project(self.client, self.id, project_name)

    @property
    def fs_url(self):
        """URL of the file storage gateway"""
        return get_fs_url(self)

    @property
    def fs_bucket_url(self):
        """URL of the project's bucket in the file storage gateway"""
        return f"{get_fs_url(self)}/{self.id}"


ProjectSchema.Meta.object_class = Project


def get_projects(client, as_objects=True, **query_params):
    """
    Returns list of projects
    """
    url = f"{client.jms_api_url}/projects"
    r = client.session.get(url, params=query_params)

    data = r.json()["projects"]
    if not as_objects:
        return data

    schema = ProjectSchema(many=True)
    projects = schema.load(data)
    for p in projects:
        p.client = client
    return projects


def get_project(client, id=None, name=None) -> Project:
    """
    Return a single project
    """
    params = {}
    if name:
        url = f"{client.jms_api_url}/projects/"
        params["name"] = name
    else:
        url = f"{client.jms_api_url}/projects/{id}"

    r = client.session.get(url, params=params)

    if len(r.json()["projects"]):
        schema = ProjectSchema()
        project = schema.load(r.json()["projects"][0])
        project.client = client
        return project
    return None


def create_project(client, project, replace=False, as_objects=True) -> Project:
    url = f"{client.jms_api_url}/projects/"

    schema = ProjectSchema()
    serialized_data = schema.dump(project)
    json_data = json.dumps({"projects": [serialized_data], "replace": replace})
    r = client.session.post(f"{url}", data=json_data)

    data = r.json()["projects"][0]
    if not as_objects:
        return data

    project = schema.load(data)
    project.client = client
    return project


def update_project(client, project, as_objects=True) -> Project:
    url = f"{client.jms_api_url}/projects/{project.id}"

    schema = ProjectSchema()
    serialized_data = schema.dump(project)
    json_data = json.dumps({"projects": [serialized_data]})
    r = client.session.put(f"{url}", data=json_data)

    data = r.json()["projects"][0]
    if not as_objects:
        return data

    project = schema.load(data)
    project.client = client
    return project


def delete_project(client, project):

    url = f"{client.jms_api_url}/projects/{project.id}"
    r = client.session.delete(url)


def copy_project(client, project_source_id, project_target_name, wait=True):

    url = f"{client.jms_api_url}/projects/{project_source_id}/copy"
    r = client.session.put(url, params={"project_name": project_target_name})

    operation_location = r.headers["location"]

    if not wait:
        return operation_location

    op = _monitor_operation(client, operation_location, 1.0)
    if not op["succeeded"]:
        raise REPError(f"Failed to copy project {project_source_id}.")
    return op["result"]


def archive_project(client, project, target_path, include_job_files=True):

    # PUT archive request
    url = f"{client.jms_api_url}/projects/{project.id}/archive"
    query_params = {}
    if not include_job_files:
        query_params["download_files"] = "job_definition"

    r = client.session.put(url, params=query_params)

    # Monitor archive operation
    operation_location = r.headers["location"]
    log.debug(f"Operation location: {operation_location}")

    op = _monitor_operation(client, operation_location, 1.0)

    if not op["succeeded"]:
        raise REPError(f"Failed to archive project {project.id}.")

    download_link = op["result"]["backend_path"]

    # Download archive
    download_link = download_link.replace("ansfs://", project.fs_url + "/")
    log.info(f"Project archive download link: {download_link}")

    if not os.path.isdir(target_path):
        raise REPError(f"Project archive: target path does not exist {target_path}")

    file_path = os.path.join(target_path, download_link.rsplit("/")[-1])
    log.info(f"Download archive to {file_path}")

    with client.session.get(download_link, stream=True) as r:
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    log.info(f"Done saving project archive to disk")
    return file_path


def restore_project(client, archive_path, project_name):

    if not os.path.exists(archive_path):
        raise REPError(f"Project archive: path does not exist {archive_path}")

    # Upload archive to FS API
    archive_name = os.path.basename(archive_path)

    bucket = f"rep-client-restore-{uuid.uuid4()}"
    fs_file_url = f"{client.rep_url}/fs/api/v1/{bucket}/{archive_name}"
    ansfs_file_url = f"ansfs://{bucket}/{archive_name}"

    fs_headers = {"content-type": "application/octet-stream"}

    log.info(f"Uploading archive to {fs_file_url}")
    with open(archive_path, "rb") as file_content:
        r = client.session.post(fs_file_url, data=file_content, headers=fs_headers)

    # POST restore request
    log.info(f"Restoring archive from {ansfs_file_url}")
    url = f"{client.jms_api_url}/projects/archive"
    query_params = {"backend_path": ansfs_file_url}
    r = client.session.post(url, params=query_params)

    # Monitor restore operation
    operation_location = r.headers["location"]
    log.debug(f"Operation location: {operation_location}")

    op = _monitor_operation(client, operation_location, 1.0)

    if not op["succeeded"]:
        raise REPError(f"Failed to restore project from archive {archive_path}.")

    project_id = op["result"]
    log.info("Done restoring project")

    # Delete archive file on server
    log.info(f"Delete file bucket {fs_file_url}")
    r = client.session.put(f"{client.rep_url}/fs/api/v1/remove/{bucket}")

    return get_project(client, project_id)


def _monitor_operation(client, location, interval=1.0):

    done = False
    op = None

    while not done:
        r = client.session.get(f"{client.jms_api_url}{location}")
        if len(r.json()["operations"]) > 0:
            op = r.json()["operations"][0]
            done = op["finished"]
            log.info(
                f"""Operation {op['name']} - progress={op['progress'] * 100.0}%,
                  succeeded={op['succeeded']}, finished={op['finished']}"""
            )
        time.sleep(interval)

    return op


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
