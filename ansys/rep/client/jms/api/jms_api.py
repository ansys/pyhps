import json
import logging
import os
import time
from typing import List, Union
import uuid

from ansys.rep.client.client import Client
from ansys.rep.client.exceptions import REPError
from ansys.rep.client.jms.resource import (
    Evaluator,
    Operation,
    Permission,
    Project,
    TaskDefinitionTemplate,
)
from ansys.rep.client.jms.schema.project import ProjectSchema

from .base import create_objects, delete_objects, get_object, get_objects, update_objects

log = logging.getLogger(__name__)


class JmsApi(object):
    """Wraps around the Job Management Service root endpoints.

    Parameters
    ----------
    client : Client
        A REP client object.

    Examples
    --------

    Create a new project

    >>> from ansys.rep.client import Client
    >>> from ansys.rep.client.jms import JmsApi, Project
    >>> cl = Client(
    ...     rep_url="https://127.0.0.1:8443/rep", username="repadmin", password="repadmin"
    ... )
    >>> jms_api = JmsApi(cl)
    >>> project = jms_api.create_project(Project(name="Example Project"))

    """

    def __init__(self, client: Client):
        self.client = client

    @property
    def url(self) -> str:
        """Returns the API url"""
        return f"{self.client.rep_url}/jms/api/v1"

    def get_api_info(self):
        """Return info like version, build date etc of the JMS API the client is connected to"""
        r = self.client.session.get(self.url)
        return r.json()

    ################################################################
    # Projects
    def get_projects(self, as_objects=True, **query_params) -> List[Project]:
        """Return a list of projects, optionally filtered by given query parameters."""
        return get_projects(self.client, self.url, as_objects, **query_params)

    def get_project(self, id: str) -> Project:
        """Return a single project for given project id."""
        return get_project(self.client, self.url, id)

    def get_project_by_name(
        self, name: str, last_created: bool = True
    ) -> Union[Project, List[Project]]:
        """Query projects by name. If no projects are found, an empty list is returned.

        In case of multiple projects with same name:

         - If ``last_created`` = True, the last created project is returned
         - If ``last_created`` = False, the full list of projects with given name is returned

        """
        return get_project_by_name(self.client, self.url, name, last_created)

    def create_project(self, project: Project, replace=False, as_objects=True) -> Project:
        """Create a new project"""
        return create_project(self.client, self.url, project, replace, as_objects)

    def update_project(self, project: Project, as_objects=True) -> Project:
        """Update an existing project"""
        return update_project(self.client, self.url, project, as_objects)

    def delete_project(self, project):
        """Delete a project"""
        return delete_project(self.client, self.url, project)

    def restore_project(self, path: str) -> Project:
        """Restore a project from an archive

        Parameters
        ----------
        path : str
            Path of the archive file to be restored.

        """
        return restore_project(self, path)

    ################################################################
    # Evaluators
    def get_evaluators(self, as_objects=True, **query_params) -> List[Evaluator]:
        """Return a list of evaluators, optionally filtered by given query parameters"""
        return get_objects(self.client.session, self.url, Evaluator, as_objects, **query_params)

    def update_evaluators(
        self, evaluators: List[Evaluator], as_objects=True, **query_params
    ) -> List[Evaluator]:
        """Update evaluators

        Examples
        --------

        You can request multiple evaluators configuration updates at once.
        This example shows how to set a custom resource property
        on all Linux evaluators that were active in the past 60 seconds.

        >>> import datetime
        >>> from ansys.rep.client import Client
        >>> from ansys.rep.client.jms import JmsApi, EvaluatorConfigurationUpdate
        >>> cl = Client(
        ...     rep_url="https://localhost:8443/rep", username="repuser", password="repuser"
        ... )
        >>> jms_api = JmsApi(cl)
        >>> query_params = {
        ...     "platform" : "linux",
        ...     "update_time.gt" : datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
        ... }
        >>> evaluators = jms_api.get_evaluators(fields=["id", "host_id"], **query_params)
        >>> config_update = EvaluatorConfigurationUpdate(
        ...    custom_resource_properties={"disk_type" : "SSD"}
        ... )
        >>> for ev in evaluators:
        ...     ev.configuration_updates = config_update
        >>> evaluators = jms_api.update_evaluators(evaluators)

        """
        return update_objects(
            self.client.session, self.url, evaluators, Evaluator, as_objects, **query_params
        )

    ################################################################
    # Task Definition Templates
    def get_task_definition_templates(
        self, as_objects=True, **query_params
    ) -> List[TaskDefinitionTemplate]:
        """Return a list of task definition templates,
        optionally filtered by given query parameters"""
        return get_objects(
            self.client.session, self.url, TaskDefinitionTemplate, as_objects, **query_params
        )

    def create_task_definition_templates(
        self, templates: List[TaskDefinitionTemplate], as_objects=True, **query_params
    ) -> List[TaskDefinitionTemplate]:
        """Create new task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return create_objects(self.client.session, self.url, templates, as_objects, **query_params)

    def update_task_definition_templates(
        self, templates: List[TaskDefinitionTemplate], as_objects=True, **query_params
    ) -> List[TaskDefinitionTemplate]:
        """Update existing task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return update_objects(
            self.client.session,
            self.url,
            templates,
            TaskDefinitionTemplate,
            as_objects,
            *query_params,
        )

    def delete_task_definition_templates(self, templates: List[TaskDefinitionTemplate]):
        """Delete existing task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return delete_objects(self.client.session, self.url, templates)

    # Task Definition Template Permissions
    def get_task_definition_template_permissions(
        self, template_id: str, as_objects: bool = True
    ) -> List[Permission]:
        """Get permissions of a task definition template"""
        return get_objects(
            self.client.session,
            f"{self.url}/task_definition_templates/{template_id}",
            Permission,
            as_objects,
        )

    def update_task_definition_template_permissions(
        self,
        template_id: str,
        permissions: List[Permission],
        as_objects: bool = True,
    ) -> List[Permission]:
        """Update permissions of a task definition template"""
        return update_objects(
            self.client.session,
            f"{self.url}/task_definition_templates/{template_id}",
            permissions,
            Permission,
            as_objects,
        )

    ################################################################
    # Operations
    def get_operations(self, as_objects=True, **query_params) -> List[Operation]:
        return get_objects(
            self.client.session, self.url, Operation, as_objects=as_objects, **query_params
        )

    def get_operation(self, id, as_object=True) -> Operation:
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


def get_project(client, api_url, id) -> Project:
    """
    Return a single project
    """

    url = f"{api_url}/projects/{id}"
    r = client.session.get(url)

    if len(r.json()["projects"]):
        schema = ProjectSchema()
        return schema.load(r.json()["projects"][0])
    return None


def get_project_by_name(client, api_url, name, last_created=True) -> Union[Project, List[Project]]:
    """
    Return a single project
    """

    params = {"name": name}
    if last_created:
        params["sort"] = "-creation_time"
        params["limit"] = 1

    projects = get_projects(client, api_url, **params)

    if len(projects) == 1:
        return projects[0]
    return projects


def create_project(client, api_url, project, replace=False, as_objects=True) -> Project:
    url = f"{api_url}/projects/"

    schema = ProjectSchema()
    serialized_data = schema.dump(project)
    json_data = json.dumps({"projects": [serialized_data], "replace": replace})
    r = client.session.post(f"{url}", data=json_data)

    if not r.json()["projects"]:
        raise REPError(f"Failed to create the project. Request response: {r.json()}")

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
            progress = None
            if op.progress is not None:
                progress = f"{op.progress * 100.0}%"
            log.info(
                f"Operation {op.name} - progress={progress}, "
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
