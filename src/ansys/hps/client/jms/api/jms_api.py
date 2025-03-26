# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

import backoff

from ansys.hps.client.check_version import JMS_VERSIONS, HpsRelease, version_required
from ansys.hps.client.client import Client
from ansys.hps.client.common import Object
from ansys.hps.client.exceptions import HPSError
from ansys.hps.client.jms.resource import Operation, Permission, Project, TaskDefinitionTemplate
from ansys.hps.client.jms.schema.project import ProjectSchema
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState

from .base import copy_objects as base_copy_objects
from .base import create_objects, delete_objects, get_object, get_objects, update_objects

log = logging.getLogger(__name__)


class JmsApi:
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
        self._api_info = None

    @property
    def url(self) -> str:
        """URL of the API."""
        return f"{self.client.url}/jms/api/v1"

    def get_api_info(self):
        """Get information of the JMS API that the client is connected to.

        Information includes the version and build date.
        """
        if self._api_info is None:
            r = self.client.session.get(self.url)
            self._api_info = r.json()
        return self._api_info

    @property
    def version(self) -> str:
        """API version."""
        return self.get_api_info()["build"]["version"]

    ################################################################
    # Projects
    def get_projects(self, as_objects=True, **query_params) -> list[Project]:
        """Get a list of projects, optionally filtered by query parameters."""
        return get_projects(self.client, self.url, as_objects, **query_params)

    def get_project(self, id: str) -> Project:
        """Get a single project for a given project ID."""
        return get_project(self.client, self.url, id)

    def get_project_by_name(self, name: str, last_created: bool = True) -> Project | list[Project]:
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

    @version_required(min_version=JMS_VERSIONS[HpsRelease.v1_2_0])
    def restore_project(self, path: str) -> Project:
        """Restore a project from an archive.

        Parameters
        ----------
        path : str
            Path of the archive file.

        """
        return _restore_project(self, path)

    ################################################################
    # Task Definition Templates
    def get_task_definition_templates(
        self, as_objects=True, **query_params
    ) -> list[TaskDefinitionTemplate]:
        """Get a list of task definition templates, optionally filtered by query parameters."""
        return get_objects(
            self.client.session, self.url, TaskDefinitionTemplate, as_objects, **query_params
        )

    def create_task_definition_templates(
        self, templates: list[TaskDefinitionTemplate], as_objects=True, **query_params
    ) -> list[TaskDefinitionTemplate]:
        """Create task definition templates."""
        return create_objects(
            self.client.session,
            self.url,
            templates,
            TaskDefinitionTemplate,
            as_objects,
            **query_params,
        )

    def update_task_definition_templates(
        self, templates: list[TaskDefinitionTemplate], as_objects=True, **query_params
    ) -> list[TaskDefinitionTemplate]:
        """Update task definition templates."""
        return update_objects(
            self.client.session,
            self.url,
            templates,
            TaskDefinitionTemplate,
            as_objects,
            *query_params,
        )

    def delete_task_definition_templates(self, templates: list[TaskDefinitionTemplate]):
        """Delete task definition templates."""
        return delete_objects(self.client.session, self.url, templates, TaskDefinitionTemplate)

    def copy_task_definition_templates(
        self, templates: list[TaskDefinitionTemplate], wait: bool = True
    ) -> str | list[str]:
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
    ) -> list[Permission]:
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
        permissions: list[Permission],
        as_objects: bool = True,
    ) -> list[Permission]:
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
    def get_operations(self, as_objects=True, **query_params) -> list[Operation]:
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
        return _get_storages(self.client, self.url)


def get_projects(client, api_url, as_objects=True, **query_params) -> list[Project]:
    """Get a list of projects."""
    url = f"{api_url}/projects"
    r = client.session.get(url, params=query_params)

    data = r.json()["projects"]
    if not as_objects:
        return data

    schema = ProjectSchema(many=True)
    return schema.load(data)


def get_project(client, api_url, id) -> Project:
    """Get a single project."""
    url = f"{api_url}/projects/{id}"
    r = client.session.get(url)

    if len(r.json()["projects"]):
        schema = ProjectSchema()
        return schema.load(r.json()["projects"][0])
    return None


def get_project_by_name(client, api_url, name, last_created=True) -> Project | list[Project]:
    """Get a single project by name."""
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
    _ = client.session.delete(url)


def _monitor_operation(
    jms_api: JmsApi, operation_id: str, max_value: float = 5.0, max_time: float = None
) -> Operation:
    """Monitor an operation."""

    @backoff.on_predicate(
        backoff.expo,
        lambda x: x[1] is False,
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
    client: Client, api_url: str, objects: list[Object], wait: bool = True
) -> str | list[str]:
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


def _restore_project(jms_api, archive_path):
    """Restore an archived project."""
    if not os.path.exists(archive_path):
        raise HPSError(f"Project archive: path does not exist {archive_path}")

    log.info(f"Uploading archive {archive_path}")

    # POST project archive dir creation request
    url = f"{jms_api.url}/projects/dir"
    r = jms_api.client.session.post(url)
    if not r.json()["project_dir"]:
        msg = "Failed to create the archive restore dir."
        msg += f" Request response: {r.json()}"
        raise HPSError(f"{msg}")
    bucket = r.json()["project_dir"][0]
    _upload_archive(jms_api, archive_path, bucket)

    # POST restore request
    log.info(f"Restoring archive {archive_path}")
    url = f"{jms_api.url}/projects/archive"
    query_params = {"backend_path": f"{bucket}/{os.path.basename(archive_path)}"}
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
    op = jms_api.client.data_transfer_api.rmdir([StoragePath(path=bucket)])
    op = jms_api.client.data_transfer_api.wait_for([op.id])
    if op[0].state != OperationState.Succeeded:
        raise HPSError(f"Delete temporary bucket {bucket} failed")

    return get_project(jms_api.client, jms_api.url, project_id)


def _upload_archive(jms_api: JmsApi, archive_path, bucket):
    """Uploads archive using data transfer worker."""  # noqa: D401
    jms_api.client.initialize_data_transfer_client()

    src = StoragePath(path=archive_path, remote="local")
    dst = StoragePath(path=f"{bucket}/{os.path.basename(archive_path)}")

    op = jms_api.client.data_transfer_api.copy([SrcDst(src=src, dst=dst)])
    op = jms_api.client.data_transfer_api.wait_for(op.id)

    log.info(f"Operation {op[0].state}")
    if op[0].state != OperationState.Succeeded:
        raise HPSError(f"Upload of archive {archive_path} failed")


def _get_storages(client: Client, api_url: str) -> list[dict]:
    """Get a list of storages."""
    url = f"{api_url}/storage"
    r = client.session.get(url)
    return r.json()["backends"]
