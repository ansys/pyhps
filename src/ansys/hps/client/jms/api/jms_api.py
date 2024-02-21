# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module wrapping around the JMS root endpoints."""
import json
import logging
import os
from typing import List, Union
import uuid

import backoff
import requests

from ansys.hps.client.client import Client
from ansys.hps.client.common import Object
from ansys.hps.client.exceptions import HPSError
from ansys.hps.client.jms.resource import Operation, Permission, Project, TaskDefinitionTemplate
from ansys.hps.client.jms.schema.project import ProjectSchema

from .base import copy_objects as base_copy_objects
from .base import create_objects, delete_objects, get_object, get_objects, update_objects

log = logging.getLogger(__name__)


class JmsApi(object):
    """Wraps around the JMS root endpoints.

    Parameters
    ----------
    client : Client
        HPS client object.

    Examples
    --------

    Create a project.

    >>> from ansys.hps.client import Client
    >>> from ansys.hps.client.jms import JmsApi, Project
    >>> cl = Client(
    ...     url="https://127.0.0.1:8443/hps", username="repuser", password="repuser"
    ... )
    >>> jms_api = JmsApi(cl)
    >>> project = jms_api.create_project(Project(name="Example project"))

    """

    def __init__(self, client: Client):
        """Initialize JMS API."""
        self.client = client
        self._fs_url = None

    @property
    def url(self) -> str:
        """URL of the API."""
        return f"{self.client.url}/jms/api/v1"

    @property
    def fs_url(self) -> str:
        """URL of the file storage gateway."""
        if self._fs_url is None:
            self._fs_url = get_fs_url(self.client, self.url)
        return self._fs_url

    def get_api_info(self):
        """Get information of the JMS API that the client is connected to.

        Information includes the version and build date.
        """
        r = self.client.session.get(self.url)
        return r.json()

    ################################################################
    # Projects
    def get_projects(self, as_objects=True, **query_params) -> List[Project]:
        """Get a list of projects, optionally filtered by query parameters."""
        return get_projects(self.client, self.url, as_objects, **query_params)

    def get_project(self, id: str) -> Project:
        """Get a single project for a given project ID."""
        return get_project(self.client, self.url, id)

    def get_project_by_name(
        self, name: str, last_created: bool = True
    ) -> Union[Project, List[Project]]:
        """Query projects by name.

        If no projects are found, an empty list is returned.

        In multiple projects with same name are found, what is returned depends
        on the ``last_created`` value:

        - If ``last_created=True``, the last created project is returned.
        - If ``last_created=False``, the full list of projects with the given name is returned.

        """
        return get_project_by_name(self.client, self.url, name, last_created)

    def create_project(self, project: Project, replace=False, as_objects=True) -> Project:
        """Create a project."""
        return create_project(self.client, self.url, project, replace, as_objects)

    def update_project(self, project: Project, as_objects=True) -> Project:
        """Update a project."""
        return update_project(self.client, self.url, project, as_objects)

    def delete_project(self, project):
        """Delete a project."""
        return delete_project(self.client, self.url, project)

    def restore_project(self, path: str) -> Project:
        """Restore a project from an archive.

        Parameters
        ----------
        path : str
            Path of the archive file.

        """
        return restore_project(self, path)

    ################################################################
    # Task Definition Templates
    def get_task_definition_templates(
        self, as_objects=True, **query_params
    ) -> List[TaskDefinitionTemplate]:
        """Get a list of task definition templates, optionally filtered by query parameters."""
        return get_objects(
            self.client.session, self.url, TaskDefinitionTemplate, as_objects, **query_params
        )

    def create_task_definition_templates(
        self, templates: List[TaskDefinitionTemplate], as_objects=True, **query_params
    ) -> List[TaskDefinitionTemplate]:
        """Create task definition templates.

        Parameters
        ----------
        templates : list of :class:`ansys.hps.client.jms.TaskDefinitionTemplate`
            List of task definition templates.
        """
        return create_objects(
            self.client.session,
            self.url,
            templates,
            TaskDefinitionTemplate,
            as_objects,
            **query_params,
        )

    def update_task_definition_templates(
        self, templates: List[TaskDefinitionTemplate], as_objects=True, **query_params
    ) -> List[TaskDefinitionTemplate]:
        """Update task definition templates.

        Parameters
        ----------
        templates : list of :class:`ansys.hps.client.jms.TaskDefinitionTemplate`
            List of task definition templates.
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
        """Delete task definition templates.

        Parameters
        ----------
        templates : list of :class:`ansys.hps.client.jms.TaskDefinitionTemplate`
            List of task definition templates.
        """
        return delete_objects(self.client.session, self.url, templates, TaskDefinitionTemplate)

    def copy_task_definition_templates(
        self, templates: List[TaskDefinitionTemplate], wait: bool = True
    ) -> Union[str, List[str]]:
        """Create task definition templates by copying existing templates.

        Parameters
        ----------
        templates : List[TaskDefinitionTemplate]
            List of task definition template. Note that only the ``id`` field of
            ``TaskDefinitionTemplate`` objects must be filled. The other fields can be empty.
        wait : bool, optional
            Whether to wait for the copy to complete. The default is ``True``.

        Returns
        -------
        Union[List[str], str]
            If ``wait=True``, returns the list of newly created template IDs.
            If ``wait=False``, returns an operation ID that can be used to
            track progress.
        """
        return _copy_objects(self.client, self.url, templates, wait=wait)

    # Task Definition Template Permissions
    def get_task_definition_template_permissions(
        self, template_id: str, as_objects: bool = True
    ) -> List[Permission]:
        """Get permissions of a task definition template."""
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
        """Update permissions of a task definition template."""
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
        """Get operations."""
        return get_objects(
            self.client.session, self.url, Operation, as_objects=as_objects, **query_params
        )

    def get_operation(self, id, as_object=True) -> Operation:
        """Get an operation."""
        return get_object(self.client.session, self.url, Operation, id, as_object=as_object)

    def monitor_operation(self, operation_id: str, max_value: float = 5.0, max_time: float = None):
        """Poll an operation until it is completed using an exponential backoff.

        Parameters
        ----------
        operation_id : str
            ID of the operation to monitor.
        max_value: float, optional
            Maximum interval in seconds between consecutive calls.
        max_time: float, optional
            Maximum time in seconds to pool the operation before giving up.
        """
        return _monitor_operation(self, operation_id, max_value, max_time)

    ################################################################
    # Storages
    def get_storage(self):
        """Get a list of storages."""
        return get_storages(self.client, self.url)


def get_projects(client, api_url, as_objects=True, **query_params) -> List[Project]:
    """
    Get a list of projects.
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
    Get a single project.
    """

    url = f"{api_url}/projects/{id}"
    r = client.session.get(url)

    if len(r.json()["projects"]):
        schema = ProjectSchema()
        return schema.load(r.json()["projects"][0])
    return None


def get_project_by_name(client, api_url, name, last_created=True) -> Union[Project, List[Project]]:
    """
    Get a single project by name.
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
    """Create a project."""
    url = f"{api_url}/projects/"

    schema = ProjectSchema()
    serialized_data = schema.dump(project)
    json_data = json.dumps({"projects": [serialized_data], "replace": replace})
    r = client.session.post(f"{url}", data=json_data)

    if not r.json()["projects"]:
        raise HPSError(f"Failed to create the project. Request response: {r.json()}")

    data = r.json()["projects"][0]
    if not as_objects:
        return data

    return schema.load(data)


def update_project(client, api_url, project, as_objects=True) -> Project:
    """Update a project."""
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
    """Delete a project."""
    url = f"{api_url}/projects/{project.id}"
    r = client.session.delete(url)


def _monitor_operation(
    jms_api: JmsApi, operation_id: str, max_value: float = 5.0, max_time: float = None
) -> Operation:
    """Monitor an operation."""

    @backoff.on_predicate(
        backoff.expo,
        lambda x: x[1] == False,
        jitter=backoff.full_jitter,
        max_value=max_value,
        max_time=max_time,
    )
    def _monitor():
        """Monitor the operation with its ID."""
        done = False
        op = jms_api.get_operation(id=operation_id)
        if op:
            done = op.finished
        return op, done

    op, done = _monitor()

    if not done:
        raise HPSError(f"Operation {operation_id} did not complete.")
    return op


def _copy_objects(
    client: Client, api_url: str, objects: List[Object], wait: bool = True
) -> Union[str, List[str]]:
    """Copy objects."""
    operation_id = base_copy_objects(client.session, api_url, objects)

    if not wait:
        return operation_id

    op = _monitor_operation(JmsApi(client), operation_id, 1.0)
    if not op.succeeded:
        obj_type = objects[0].__class__
        rest_name = obj_type.Meta.rest_name
        raise HPSError(f"Failed to copy {rest_name} with ids = {[obj.id for obj in objects]}.")
    return op.result["destination_ids"]


def restore_project(jms_api, archive_path):
    """Restore an archived project."""
    if not os.path.exists(archive_path):
        raise HPSError(f"Project archive: path does not exist {archive_path}")

    # Upload archive to FS API
    archive_name = os.path.basename(archive_path)

    bucket = f"hps-client-restore-{uuid.uuid4()}"
    fs_file_url = f"{jms_api.client.url}/fs/api/v1/{bucket}/{archive_name}"
    ansfs_file_url = f"ansfs://{bucket}/{archive_name}"  # noqa: E231

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

    op = jms_api.monitor_operation(operation_id)

    if not op.succeeded:
        raise HPSError(f"Failed to restore project from archive {archive_path}.")

    project_id = op.result["project_id"]
    log.info(f"Done restoring project, project_id = '{project_id}'")

    # Delete archive file on server
    log.info(f"Delete temporary bucket {bucket}")
    r = jms_api.client.session.put(f"{jms_api.client.url}/fs/api/v1/remove/{bucket}")

    return get_project(jms_api.client, jms_api.url, project_id)


def get_storages(client, api_url):
    """
    Get a list of storages.
    """
    url = f"{api_url}/storage"
    r = client.session.get(url)
    return r.json()["backends"]


def get_fs_url(client, api_url):
    """Get the file storage URL."""
    file_storages = get_storages(client, api_url)

    if not file_storages:
        raise HPSError(f"There is no file storage information.")

    rest_gateways = [fs for fs in file_storages if fs["obj_type"] == "RestGateway"]
    rest_gateways.sort(key=lambda fs: fs["priority"])

    if not rest_gateways:
        raise HPSError(f"There is no REST gateway defined.")

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
