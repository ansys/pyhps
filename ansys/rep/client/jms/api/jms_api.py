import json
import logging
import os
import time
from typing import List
import uuid

from ansys.rep.client.exceptions import REPError

from ..resource import Operation
from ..resource.evaluator import Evaluator
from ..resource.project import Project, ProjectSchema
from ..resource.task_definition_template import TaskDefinitionTemplate
from .base import create_objects, delete_objects, get_object, get_objects, update_objects

log = logging.getLogger(__name__)


class JmsApi(object):
    """Root API

    Args:
        client (:class:`ansys.rep.client.jms.Client`): A client object.

    Example:

        >>> from ansys.rep.client.jms import Client
        >>> # Create client object and connect to REP with username & password
        >>> cl = Client(rep_url="https://127.0.0.1/dcs", username="repadmin", password="repadmin")
        >>> # Create a new project
        >>> root_api = RootApi(client)
        >>> project = root_api.create_project(Project(name="Example Project"))

    """

    def __init__(self, client):
        self.client = client

    @property
    def url(self):
        return f"{self.client.rep_url}/jms/api/v1"

    ################################################################
    # Projects
    def get_projects(self, **query_params):
        """Return a list of projects, optionally filtered by given query parameters"""
        return get_projects(self.client, self.url, **query_params)

    def get_project(self, id=None, name=None):
        """Return a single project for given project id"""
        return get_project(self.client, self.url, id, name)

    def create_project(self, project, replace=False, as_objects=True):
        """Create a new project"""
        return create_project(self.client, self.url, project, replace, as_objects)

    def update_project(self, project, as_objects=True):
        """Update an existing project"""
        return update_project(self.client, self.url, project, as_objects)

    def delete_project(self, project):
        """Delete a project"""
        return delete_project(self.client, self.url, project)

    def restore_project(self, path: str) -> Project:
        """Restore a project from an archive

        Args:
            path (str): Path of the archive file to be restored.
            project_name (str): Name of the restored project. (optional)

        Returns:
            :class:`ansys.rep.client.jms.Project`: A Project object.
        """
        return restore_project(self, path)

    ################################################################
    # Evaluators
    def get_evaluators(self, as_objects=True, **query_params):
        """Return a list of evaluators, optionally filtered by given query parameters"""
        return get_objects(self.client.session, self.url, Evaluator, as_objects, **query_params)

    def update_evaluators(self, evaluators, as_objects=True, **query_params):
        """Update evaluators configuration"""
        return update_objects(self.client.session, self.url, evaluators, as_objects, **query_params)

    ################################################################
    # Task Definition Templates
    def get_task_definition_templates(self, as_objects=True, **query_params):
        """Return a list of task definition templates,
        optionally filtered by given query parameters"""
        return get_objects(
            self.client.session, self.url, TaskDefinitionTemplate, as_objects, **query_params
        )

    def create_task_definition_templates(self, templates, as_objects=True, **query_params):
        """Create new task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return create_objects(self.client.session, self.url, templates, as_objects, **query_params)

    def update_task_definition_templates(self, templates, as_objects=True, **query_params):
        """Update existing task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return update_objects(self.client.session, self.url, templates, as_objects, **query_params)

    def delete_task_definition_templates(self, templates):
        """Delete existing task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return delete_objects(self.client.session, self.url, templates)

    ################################################################
    # Operations
    def get_operations(self, as_objects=True, **query_params):
        return get_objects(
            self.client.session, self.url, Operation, as_objects=as_objects, **query_params
        )

    def get_operation(self, id, as_object=True):
        return get_object(self.client.session, self.url, Operation, id, as_object=as_object)

    def _monitor_operation(self, operation_id: str, interval: float = 1.0):
        return _monitor_operation(self, operation_id, interval)


def get_projects(client, api_url, as_objects=True, **query_params) -> List[Project]:
    """
    Returns list of projects
    """
    url = f"{api_url}/projects"
    r = client.session.get(url, params=query_params)

    data = r.json()["projects"]
    if not as_objects:
        return data

    schema = ProjectSchema(many=True)
    return schema.load(data)


def get_project(client, api_url, id=None, name=None) -> Project:
    """
    Return a single project
    """
    params = {}
    if name:
        url = f"{api_url}/projects/"
        params["name"] = name
    else:
        url = f"{api_url}/projects/{id}"

    r = client.session.get(url, params=params)

    if len(r.json()["projects"]):
        schema = ProjectSchema()
        return schema.load(r.json()["projects"][0])
    return None


def create_project(client, api_url, project, replace=False, as_objects=True) -> Project:
    url = f"{api_url}/projects/"

    schema = ProjectSchema()
    serialized_data = schema.dump(project)
    json_data = json.dumps({"projects": [serialized_data], "replace": replace})
    r = client.session.post(f"{url}", data=json_data)

    data = r.json()["projects"][0]
    if not as_objects:
        return data

    return schema.load(data)


def update_project(client, api_url, project, as_objects=True) -> Project:
    url = f"{api_url}/projects/{project.id}"

    schema = ProjectSchema()
    serialized_data = schema.dump(project)
    json_data = json.dumps({"projects": [serialized_data]})
    r = client.session.put(f"{url}", data=json_data)

    data = r.json()["projects"][0]
    if not as_objects:
        return data

    return schema.load(data)


def delete_project(client, api_url, project):

    url = f"{api_url}/projects/{project.id}"
    r = client.session.delete(url)


def _monitor_operation(jms_api: JmsApi, operation_id: str, interval: float = 1.0):

    done = False
    op = None
    while not done:
        op = jms_api.get_operation(id=operation_id)
        if op:
            done = op.finished
            log.info(
                f"Operation {op.name} - progress={op.progress * 100.0}%, "
                f"succeeded={op.succeeded}, finished={op.finished}"
            )
        time.sleep(interval)
    return op


def restore_project(jms_api, archive_path):

    if not os.path.exists(archive_path):
        raise REPError(f"Project archive: path does not exist {archive_path}")

    # Upload archive to FS API
    archive_name = os.path.basename(archive_path)

    bucket = f"rep-client-restore-{uuid.uuid4()}"
    fs_file_url = f"{jms_api.client.rep_url}/fs/api/v1/{bucket}/{archive_name}"
    ansfs_file_url = f"ansfs://{bucket}/{archive_name}"

    fs_headers = {"content-type": "application/octet-stream"}

    log.info(f"Uploading archive to {fs_file_url}")
    with open(archive_path, "rb") as file_content:
        r = jms_api.client.session.post(fs_file_url, data=file_content, headers=fs_headers)

    # POST restore request
    log.info(f"Restoring archive from {ansfs_file_url}")
    url = f"{jms_api.url}/projects/archive"
    query_params = {"backend_path": ansfs_file_url}
    r = jms_api.client.session.post(url, params=query_params)

    # Monitor restore operation
    operation_location = r.headers["location"]
    log.debug(f"Operation location: {operation_location}")
    operation_id = operation_location.rsplit("/", 1)[-1]
    log.debug(f"Operation id: {operation_id}")

    op = _monitor_operation(jms_api, operation_id, 1.0)

    if not op.succeeded:
        raise REPError(f"Failed to restore project from archive {archive_path}.")

    project_id = op.result["project_id"]
    log.info(f"Done restoring project, project_id = '{project_id}'")

    # Delete archive file on server
    log.info(f"Delete temporary bucket {bucket}")
    r = jms_api.client.session.put(f"{jms_api.client.rep_url}/fs/api/v1/remove/{bucket}")

    return get_project(jms_api.client, jms_api.url, project_id)