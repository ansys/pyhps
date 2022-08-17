import json
import logging
from typing import List

from ..client import Client
from ..resource.evaluator import Evaluator
from ..resource.project import Project, ProjectSchema
from ..resource.task_definition_template import TaskDefinitionTemplate
from .base import create_objects, delete_objects, get_objects, update_objects

log = logging.getLogger(__name__)


class RootApi(object):
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

    def __init__(self, client: Client):
        self.client = client

    @property
    def url(self):
        return self.client.jms_api_url

    def get_projects(self, **query_params):
        """Return a list of projects, optionally filtered by given query parameters"""
        return get_projects(self.client, **query_params)

    def get_project(self, id=None, name=None):
        """Return a single project for given project id"""
        return get_project(self.client, id, name)

    def create_project(self, project, replace=False, as_objects=True):
        """Create a new project"""
        return create_project(self.client, project, replace, as_objects)

    def update_project(self, project, as_objects=True):
        """Update an existing project"""
        return update_project(self.client, project, as_objects)

    def delete_project(self, project):
        """Delete a project"""
        return delete_project(self.client, project)

    def restore_project(self, path, project_name):
        """Restore a project from an archive

        Args:
            path (str): Path of the archive file to be restored.
            project_id (str): ID of the restored project.

        Returns:
            :class:`ansys.rep.client.jms.Project`: A Project object.
        """
        raise NotImplementedError

    def get_evaluators(self, as_objects=True, **query_params):
        """Return a list of evaluators, optionally filtered by given query parameters"""
        return get_objects(self.client.session, self.url, Evaluator, as_objects, **query_params)

    def update_evaluators(self, evaluators, as_objects=True, **query_params):
        """Update evaluators configuration"""
        return update_objects(self.client.session, self.url, evaluators, as_objects, **query_params)

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


def get_projects(client, as_objects=True, **query_params) -> List[Project]:
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
