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

"""Module exposing the project endpoints of the JMS."""

import io
import json
import logging
import os
import tempfile
import warnings
from collections.abc import Callable

from ansys.hps.client.check_version import (
    JMS_VERSIONS,
    HpsRelease,
    check_version_and_raise,
    version_required,
)
from ansys.hps.client.client import Client
from ansys.hps.client.common import Object
from ansys.hps.client.exceptions import ClientError, HPSError
from ansys.hps.client.jms.resource import (
    Algorithm,
    File,
    Job,
    JobDefinition,
    JobSelection,
    LicenseContext,
    ParameterDefinition,
    ParameterMapping,
    Permission,
    Project,
    Task,
    TaskCommand,
    TaskCommandDefinition,
    TaskDefinition,
)
from ansys.hps.client.rms.api import RmsApi
from ansys.hps.client.rms.models import AnalyzeRequirements, AnalyzeResponse
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState

from .base import create_objects, delete_objects, get_objects, update_objects
from .jms_api import JmsApi, _copy_objects

log = logging.getLogger(__name__)


class ProjectApi:
    """Exposes the project endpoints of the JMS.

    Parameters
    ----------
    client : Client
        HPS client object.
    project_id : str
        ID of the project.

    Examples
    --------
    >>> from ansys.hps.client import Client
    >>> from ansys.hps.client.jms import JmsApi, Project, ProjectApi
    >>> cl = Client(
    ...     url="https://127.0.0.1:8443/hps", username="repuser", password="repuser"
    ... )
    >>> project = Project(name="Example project")
    >>> print(project)
    {
        "name": "Example project"
    }
    >>> jms_api = JmsApi(cl)
    >>> project = jms_api.create_project(project)
    >>> print(project)
    {
        "id": "02qtyJfpfAQ0fr3zkoIAfC",
        "name": "Example project",
        "active": false,
        "priority": 1,
        "creation_time": ...
        ...
    }
    >>> project_api = ProjectApi(cl, project.id)
    >>> print(project_api)
    'https://127.0.0.1:8443/hps/jms/api/v1/projects/02qtyJfpfAQ0fr3zkoIAfC'
    >>> jobs = project_api.get_jobs()

    """

    def __init__(self, client: Client, project_id: str):
        """Initialize project API."""
        self.client = client
        self.project_id = project_id
        self._jms_api = JmsApi(self.client)

    @property
    def jms_api_url(self) -> str:
        """Get the JMS API URL."""
        return f"{self.client.url}/jms/api/v1"

    @property
    def url(self) -> str:
        """URL of the API."""
        return f"{self.jms_api_url}/projects/{self.project_id}"

    @property
    def version(self) -> str:
        """API version."""
        return self._jms_api.version

    ################################################################
    # Project operations (copy, archive)
    def copy_project(self, wait: bool = True) -> str:
        """Duplicate the project."""
        r = copy_projects(self, [self.project_id], wait)
        if wait:
            return r[0]
        else:
            return r

    @version_required(min_version=JMS_VERSIONS[HpsRelease.v1_2_0])
    def archive_project(self, path: str, include_job_files: bool = True):
        """Archive a project and save it to disk.

        Parameters
        ----------
        path : str
            Path for saving the archive locally.
        include_job_files : bool, optional
            Whether to include job files in the archive. The default is ``True``.

        Returns
        -------
        str
            Path to the archive.

        """
        return archive_project(self, path, include_job_files)

    ################################################################
    # Files
    def get_files(self, as_objects=True, content=False, **query_params) -> list[File]:
        """Get a list of file resources, optionally filtered by query parameters.

        If ``content=True``, each file's content is also downloaded and stored in memory
        as the :attr:`ansys.hps.client.jms.File.content` attribute.
        """
        if content:
            min_v = JMS_VERSIONS[HpsRelease.v1_2_0]
            check_version_and_raise(
                self.version,
                min_version=min_v,
                msg=(
                    f"ProjectApi.get_files with content=True requires JMS version {min_v} or later."
                ),
            )

        return get_files(self, as_objects=as_objects, content=content, **query_params)

    def create_files(self, files: list[File], as_objects=True) -> list[File]:
        """Create a list of files."""
        return create_files(self, files, as_objects=as_objects)

    def update_files(self, files: list[File], as_objects=True):
        """Update files."""
        return update_files(self, files, as_objects=as_objects)

    def delete_files(self, files: list[File]):
        """Delete files."""
        return self._delete_objects(files, File)

    @version_required(min_version=JMS_VERSIONS[HpsRelease.v1_2_0])
    def download_file(
        self,
        file: File,
        target_path: str,
        stream: bool = None,
        progress_handler: Callable[[int], None] = None,
    ) -> str:
        """Download file content and save it to disk.

        If ``stream=True``, data is retrieved in chunks, which avoids storing the entire content
        in memory.
        """
        if stream is not None:
            msg = "The 'stream' input argument in ProjectApi.download_file() is deprecated. "
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            log.warning(msg)
        return _download_file(self, file, target_path, progress_handler)

    ################################################################
    # Parameter definitions
    def get_parameter_definitions(
        self, as_objects=True, **query_params
    ) -> list[ParameterDefinition]:
        """Get a list of parameter definitions."""
        return self._get_objects(ParameterDefinition, as_objects, **query_params)

    def create_parameter_definitions(
        self, parameter_definitions: list[ParameterDefinition], as_objects=True
    ) -> list[ParameterDefinition]:
        """Create a list of parameter definitions."""
        return self._create_objects(parameter_definitions, ParameterDefinition, as_objects)

    def update_parameter_definitions(
        self, parameter_definitions: list[ParameterDefinition], as_objects=True
    ) -> list[ParameterDefinition]:
        """Update a list of parameter definitions."""
        return self._update_objects(parameter_definitions, ParameterDefinition, as_objects)

    def delete_parameter_definitions(self, parameter_definitions: list[ParameterDefinition]):
        """Delete a list of parameter definitions."""
        return self._delete_objects(parameter_definitions, ParameterDefinition)

    ################################################################
    # Parameter mappings
    def get_parameter_mappings(self, as_objects=True, **query_params) -> list[ParameterMapping]:
        """Get a list of parameter mappings."""
        return self._get_objects(ParameterMapping, as_objects=as_objects, **query_params)

    def create_parameter_mappings(
        self, parameter_mappings: list[ParameterMapping], as_objects=True
    ) -> list[ParameterMapping]:
        """Get a list of created parameter mappings."""
        return self._create_objects(parameter_mappings, ParameterMapping, as_objects=as_objects)

    def update_parameter_mappings(
        self, parameter_mappings: list[ParameterMapping], as_objects=True
    ) -> list[ParameterMapping]:
        """Get a list of updated parameter mappings."""
        return self._update_objects(parameter_mappings, ParameterMapping, as_objects=as_objects)

    def delete_parameter_mappings(self, parameter_mappings: list[ParameterMapping]):
        """Delete a list of parameter mappings."""
        return self._delete_objects(parameter_mappings, ParameterMapping)

    ################################################################
    # Task definitions
    def get_task_definitions(self, as_objects=True, **query_params) -> list[TaskDefinition]:
        """Get a list of task definitions."""
        return self._get_objects(TaskDefinition, as_objects=as_objects, **query_params)

    def create_task_definitions(
        self, task_definitions: list[TaskDefinition], as_objects=True
    ) -> list[TaskDefinition]:
        """Create a list of task definitions."""
        return self._create_objects(task_definitions, TaskDefinition, as_objects=as_objects)

    def update_task_definitions(
        self, task_definitions: list[TaskDefinition], as_objects=True
    ) -> list[TaskDefinition]:
        """Update a list of task definitions."""
        return self._update_objects(task_definitions, TaskDefinition, as_objects=as_objects)

    def delete_task_definitions(self, task_definitions: list[TaskDefinition]):
        """Delete a list of task definitions."""
        return self._delete_objects(task_definitions, TaskDefinition)

    def copy_task_definitions(
        self, task_definitions: list[TaskDefinition], wait: bool = True
    ) -> str | list[str]:
        """Create task definitions by copying existing task definitions.

        Parameters
        ----------
        task_definitions : List[TaskDefinition]
            List of task definitions. Note that only the ``id`` field of the
            ``TaskDefinition`` objects must be filled. Other fields can be empty.
        wait : bool
            Whether to wait for the copy to complete. The default is ``True``.

        Returns
        -------
        Union[List[str], str]
            If ``wait=True``, returns the list of newly created task definition IDs.
            If ``wait=False``, returns an operation ID that can be used to
            track progress.

        """
        return _copy_objects(self.client, self.url, task_definitions, wait=wait)

    def get_task_command_definitions(
        self, as_objects: bool = True, **query_params
    ) -> list[TaskCommandDefinition]:
        """Get the list of task command definitions."""
        return self._get_objects(TaskCommandDefinition, as_objects=as_objects, **query_params)

    def analyze_task_definition(
        self,
        task_definition_id: str,
        evaluator_ids: list[str] = None,
        scaler_ids: list[str] = None,
        analytics: bool = True,
        as_object: bool = True,
    ) -> AnalyzeResponse:
        """Compare resource requirements against available compute resources."""
        # Task definition is retrieved as a native dictionary to more easily translate
        # the subobjects into RMS models
        tds = self.get_task_definitions(id=task_definition_id, fields="all", as_objects=False)
        if not tds:
            raise ClientError(f"Could not retrieve task definition {task_definition_id}")
        td = tds[0]

        project_permissions = self.get_permissions(as_objects=False)

        requirements = AnalyzeRequirements(
            project_id=self.project_id,
            software_requirements=td["software_requirements"],
            resource_requirements=td["resource_requirements"],
            evaluator_ids=evaluator_ids,
            scaler_ids=scaler_ids,
            project_permissions=project_permissions,
        )

        rms_api = RmsApi(self.client)
        return rms_api.analyze(requirements=requirements, analytics=analytics, as_object=as_object)

    ################################################################
    # Job definitions
    def get_job_definitions(self, as_objects=True, **query_params) -> list[JobDefinition]:
        """Get a list of job definitions."""
        return self._get_objects(JobDefinition, as_objects=as_objects, **query_params)

    def create_job_definitions(
        self, job_definitions: list[JobDefinition], as_objects=True
    ) -> list[JobDefinition]:
        """Create a list of job definitions."""
        return self._create_objects(job_definitions, JobDefinition, as_objects=as_objects)

    def update_job_definitions(
        self, job_definitions: list[JobDefinition], as_objects=True
    ) -> list[JobDefinition]:
        """Update a list of job definitions."""
        return self._update_objects(job_definitions, JobDefinition, as_objects=as_objects)

    def delete_job_definitions(self, job_definitions: list[JobDefinition]):
        """Delete a list of job definitions."""
        return self._delete_objects(job_definitions, JobDefinition)

    def copy_job_definitions(
        self, job_definitions: list[JobDefinition], wait: bool = True
    ) -> str | list[str]:
        """Create job definitions by copying existing job definitions.

        Parameters
        ----------
        job_definitions : List[JobDefinition]
            List of job definitions. Note that only the ``id`` field of the
            ``JobDefinition`` objects must be filled. The other fields can be empty.
        wait : bool
            Whether to wait for the copy to complete. The default is ``True``.

        Returns
        -------
        Union[List[str], str]
            If ``wait=True``, returns the list of newly created job definition IDs.
            If ``wait=False``, returns an operation ID that can be used to
            track progress.

        """
        return _copy_objects(self.client, self.url, job_definitions, wait=wait)

    ################################################################
    # Jobs
    def get_jobs(self, as_objects=True, **query_params) -> list[Job]:
        """Get a list of jobs."""
        return self._get_objects(Job, as_objects=as_objects, **query_params)

    def create_jobs(self, jobs: list[Job], as_objects=True) -> list[Job]:
        """Create jobs.

        Parameters
        ----------
        jobs : list of :class:`ansys.hps.client.jms.Job`
            List of jobs.
        as_objects : bool, optional
            Whether to return jobs as objects. The default is ``True``. If
            ``False``, jobs are returned as dictionaries.

        Returns
        -------
        list
            List of :class:`ansys.hps.client.jms.Job` objects if ``as_objects=True`` or
            a list of dictionaries if ``as_objects=False``.

        """
        return self._create_objects(jobs, Job, as_objects=as_objects)

    def copy_jobs(self, jobs: list[Job], wait: bool = True) -> str | list[str]:
        """Create jobs by copying existing jobs.

        Parameters
        ----------
        jobs : List[Job]
            List of jobs. Note that only the ``id`` field of the
            ``Job`` objects must be filled. The other fields can be empty.
        wait : bool, optional
            Whether to wait for the copy to complete. The default is ``True``.

        Returns
        -------
        Union[List[str], str]
            If ``wait=True``, returns the list of newly created job IDs.
            If ``wait=False``, returns an operation ID that can be used to
            track progress.

        """
        return _copy_objects(self.client, self.url, jobs, wait=wait)

    def update_jobs(self, jobs: list[Job], as_objects=True) -> list[Job]:
        """Update jobs.

        Parameters
        ----------
        jobs : list of :class:`ansys.hps.client.jms.Job`)
            List of jobs.
        as_objects : bool, optional
            Whether to return jobs as objects. The default is ``True``.
            If ``False``, jobs are returned as dictionaries.

        Returns
        -------
        list
            List of :class:`ansys.hps.client.jms.Job` objects if ``as_objects=True`` or a list of
            dictionaries if ``as_objects=False``.

        """
        return self._update_objects(jobs, Job, as_objects=as_objects)

    def delete_jobs(self, jobs: list[Job]):
        """Delete jobs.

        Parameters
        ----------
        jobs : list of :class:`ansys.hps.client.jms.Job`
            List of `jobs. Note that only the ``id`` field of the ``Job`` objects must be filled.
            The other fields can be empty.

        Example:

            >>> jobs_to_delete = []
            >>> for id in [1,2,39,44]:
            >>>    jobs_to_delete.append(Job(id=id))
            >>> project_api.delete_jobs(jobs_to_delete)

        """
        return self._delete_objects(jobs, Job)

    def sync_jobs(self, jobs: list[Job]):
        """Sync a list of jobs."""
        return sync_jobs(self, jobs)

    def _sync_jobs(self, jobs: list[Job]):
        """Sync a list of jobs (deprecated)."""
        msg = (
            "'ProjectApi._sync_jobs' is deprecated and is to be removed soon. "
            "Use 'ProjectApi.sync_jobs' instead."
        )
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        log.warning(msg)
        return self.sync_jobs(jobs)

    ################################################################
    # Tasks
    def get_tasks(self, as_objects=True, **query_params) -> list[Task]:
        """Get a list of tasks."""
        return self._get_objects(Task, as_objects=as_objects, **query_params)

    def update_tasks(self, tasks: list[Task], as_objects=True) -> list[Task]:
        """Update a list of tasks."""
        return self._update_objects(tasks, Task, as_objects=as_objects)

    ################################################################
    # Commands
    def queue_task_command(self, task_id: str, name: str, **command_arguments) -> TaskCommand:
        """Queue a command to a task."""
        # get the task definition id
        task = self.get_tasks(id=task_id, fields=["id", "task_definition_id"])[0]

        # get the command definition
        command_definitions = self.get_task_command_definitions(
            task_definition_id=task.task_definition_id, name=name
        )

        if not command_definitions:
            raise ClientError(f"Could not find a command named '{name}' for task {task_id}.")

        command_definition = None
        for cd in command_definitions:
            if cd.parameters is None:
                continue
            if set(command_arguments.keys()) == set(cd.parameters.keys()):
                command_definition = cd
                break

        if command_definition is None:
            raise ClientError(
                f"Could not find a command '{name}' with matching arguments for task {task_id}."
            )

        # create the command object
        command = TaskCommand(
            task_id=task_id,
            command_definition_id=command_definition.id,
            arguments=command_arguments,
        )
        return self.create_task_commands([command])[0]

    def get_task_commands(self, as_objects: bool = True, **query_params) -> list[TaskCommand]:
        """Get a list of task commands."""
        return self._get_objects(TaskCommand, as_objects=as_objects, **query_params)

    def create_task_commands(
        self, commands: list[TaskCommand], as_objects: bool = True
    ) -> list[TaskCommand]:
        """Create task commands."""
        return self._create_objects(commands, TaskCommand, as_objects=as_objects)

    ################################################################
    # Selections
    def get_job_selections(self, as_objects=True, **query_params) -> list[JobSelection]:
        """Get a list of job selections."""
        return self._get_objects(JobSelection, as_objects=as_objects, **query_params)

    def create_job_selections(
        self, selections: list[JobSelection], as_objects=True
    ) -> list[JobSelection]:
        """Create a list of job selections."""
        return self._create_objects(selections, JobSelection, as_objects=as_objects)

    def update_job_selections(
        self, selections: list[JobSelection], as_objects=True
    ) -> list[JobSelection]:
        """Update a list of job selections."""
        return self._update_objects(selections, JobSelection, as_objects=as_objects)

    def delete_job_selections(self, selections: list[JobSelection]):
        """Delete a list of job selections."""
        return self._delete_objects(selections, JobSelection)

    ################################################################
    # Algorithms
    def get_algorithms(self, as_objects=True, **query_params) -> list[Algorithm]:
        """Get a list of algorithms."""
        return self._get_objects(Algorithm, as_objects=as_objects, **query_params)

    def create_algorithms(self, algorithms: list[Algorithm], as_objects=True) -> list[Algorithm]:
        """Create a list of algorithms."""
        return self._create_objects(algorithms, Algorithm, as_objects=as_objects)

    def update_algorithms(self, algorithms: list[Algorithm], as_objects=True) -> list[Algorithm]:
        """Update a list of algorithms."""
        return self._update_objects(algorithms, Algorithm, as_objects=as_objects)

    def delete_algorithms(self, algorithms: list[Algorithm]):
        """Delete a list of algorithms."""
        return self._delete_objects(algorithms, Algorithm)

    ################################################################
    # Permissions
    def get_permissions(self, as_objects=True) -> list[Permission]:
        """Get a list of permissions."""
        return self._get_objects(Permission, as_objects=as_objects, fields=None)

    def update_permissions(self, permissions: list[Permission], as_objects=True):
        """Update a list of permissions."""
        return self._update_objects(permissions, Permission, as_objects=as_objects)

    ################################################################
    # License contexts
    def get_license_contexts(self, as_objects=True, **query_params) -> list[LicenseContext]:
        """Get a list of license contexts."""
        return self._get_objects(self, LicenseContext, as_objects=as_objects, **query_params)

    def create_license_contexts(self, as_objects=True) -> list[LicenseContext]:
        """Create a list of license contexts."""
        rest_name = LicenseContext.Meta.rest_name
        url = f"{self.jms_api_url}/projects/{self.project_id}/{rest_name}"
        r = self.client.session.post(f"{url}")
        data = r.json()[rest_name]
        if not as_objects:
            return data
        schema = LicenseContext.Meta.schema(many=True)
        objects = schema.load(data)
        return objects

    def update_license_contexts(self, license_contexts, as_objects=True) -> list[LicenseContext]:
        """Update a list of license contexts."""
        return self._update_objects(self, license_contexts, LicenseContext, as_objects=as_objects)

    def delete_license_contexts(self):
        """Delete license contexts."""
        rest_name = LicenseContext.Meta.rest_name
        url = f"{self.jms_api_url}/projects/{self.id}/{rest_name}"
        _ = self.client.session.delete(url)

    ################################################################

    @version_required(min_version=JMS_VERSIONS[HpsRelease.v1_2_0])
    def copy_default_execution_script(self, filename: str) -> File:
        """Copy a default execution script to the current project.

        Example:
        -------
            >>> file = project_api.copy_default_execution_script("exec_mapdl.py")

        """
        # create file resource
        name = os.path.splitext(filename)[0]
        file = File(name=name, evaluation_path=filename, type="application/x-python-code")
        file = self.create_files([file])[0]

        # query location of default execution scripts from server
        info = self._jms_api.get_api_info()
        execution_script_default_bucket = info["settings"]["execution_script_default_bucket"]

        # server side copy of the file to project bucket
        self.client.initialize_data_transfer_client()
        src = StoragePath(path=f"{execution_script_default_bucket}/{filename}")
        dst = StoragePath(path=f"{self.project_id}/{file.storage_id}")
        log.info(f"Copying default execution script {filename}")
        op = self.client.data_transfer_api.copy([SrcDst(src=src, dst=dst)])
        op = self.client.data_transfer_api.wait_for(op.id)[0]
        log.debug(f"Operation {op.state}")
        if op.state != OperationState.Succeeded:
            raise HPSError(f"Copying of default execution script {filename} failed")

        # get checksum of copied file
        op = self.client.data_transfer_api.get_metadata([dst])
        op = self.client.data_transfer_api.wait_for(op.id)[0]
        log.debug(f"Operation {op.state}")
        if op.state != OperationState.Succeeded:
            raise HPSError(
                f"Retrieval of meta data of copied default execution script {filename} failed"
            )
        checksum = op.result[dst.path]["checksum"]

        # update file resource
        file.hash = checksum
        return self.update_files([file])[0]

    ################################################################
    def _get_objects(self, obj_type: Object, as_objects=True, **query_params):
        """Get objects."""
        return get_objects(self.client.session, self.url, obj_type, as_objects, **query_params)

    def _create_objects(
        self, objects: list[Object], obj_type: type[Object], as_objects=True, **query_params
    ):
        """Create objects."""
        return create_objects(
            self.client.session, self.url, objects, obj_type, as_objects, **query_params
        )

    def _update_objects(
        self, objects: list[Object], obj_type: type[Object], as_objects=True, **query_params
    ):
        """Update objects."""
        return update_objects(
            self.client.session, self.url, objects, obj_type, as_objects, **query_params
        )

    def _delete_objects(self, objects: list[Object], obj_type: type[Object]):
        """Delete objects."""
        delete_objects(self.client.session, self.url, objects, obj_type)


def _download_files(project_api: ProjectApi, files: list[File]):
    """Download files directly using data transfer worker."""
    temp_dir = tempfile.TemporaryDirectory()

    project_api.client.initialize_data_transfer_client()
    out_path = os.path.join(temp_dir.name, "downloads")

    base_dir = project_api.project_id
    srcs = []
    dsts = []
    for f in files:
        if getattr(f, "hash", None) is not None:
            fpath = os.path.join(out_path, f"{f.id}")
            download_path = os.path.join(fpath, f.evaluation_path)
            srcs.append(StoragePath(path=f"{base_dir}/{os.path.basename(f.storage_id)}"))
            dsts.append(StoragePath(path=download_path, remote="local"))

    if len(srcs) > 0:
        log.info("Downloading files")
        op = project_api.client.data_transfer_api.copy(
            [SrcDst(src=src, dst=dst) for src, dst in zip(srcs, dsts, strict=False)]
        )
        op = project_api.client.data_transfer_api.wait_for([op.id])
        log.info(f"Operation {op[0].state}")
        if op[0].state == OperationState.Succeeded:
            for f in files:
                if getattr(f, "hash", None) is not None:
                    fpath = os.path.join(out_path, f"{f.id}")
                    download_path = os.path.join(fpath, f.evaluation_path)
                    with open(download_path, "rb") as inp:
                        f.content = inp.read()
        else:
            log.error("Download of files failed")
            raise HPSError("Download of files failed")


def get_files(project_api: ProjectApi, as_objects=True, content=False, **query_params):
    """Get files for the project API."""
    files = get_objects(
        project_api.client.session, project_api.url, File, as_objects=as_objects, **query_params
    )
    if content:
        _download_files(project_api, files)
    return files


def _upload_files(project_api: ProjectApi, files):
    """Upload files directly using the data transfer worker."""
    min_v = JMS_VERSIONS[HpsRelease.v1_2_0]
    check_version_and_raise(
        project_api.version,
        min_version=min_v,
        msg=f"Uploading file content requires JMS version {min_v} or later.",
    )

    project_api.client.initialize_data_transfer_client()
    srcs = []
    dsts = []
    base_dir = project_api.project_id
    file_path = ""

    temp_dir = tempfile.TemporaryDirectory()

    for f in files:
        if getattr(f, "src", None) is None:
            continue
        file_path = f.src
        if isinstance(f.src, io.IOBase):
            mode = "wb" if isinstance(f.src, io.BytesIO) else "w"
            with open(os.path.join(temp_dir.name, f.storage_id), mode) as out:
                out.write(f.src.getvalue())
            file_path = os.path.join(temp_dir.name, f.storage_id)
        srcs.append(StoragePath(path=file_path, remote="local"))
        dsts.append(StoragePath(path=f"{base_dir}/{os.path.basename(f.storage_id)}"))

    if len(srcs) > 0:
        log.info("Uploading files")
        op = project_api.client.data_transfer_api.copy(
            [SrcDst(src=src, dst=dst) for src, dst in zip(srcs, dsts, strict=False)]
        )
        op = project_api.client.data_transfer_api.wait_for(op.id)
        log.info(f"Operation {op[0].state}")
        if op[0].state == OperationState.Succeeded:
            _fetch_file_metadata(project_api, files, dsts)
        else:
            log.error("Upload of files failed")
            raise HPSError("Upload of files failed")

    else:
        log.info("No files to upload")


def _fetch_file_metadata(
    project_api: ProjectApi, files: list[File], storage_paths: list[StoragePath]
):
    log.info("Getting upload file metadata")
    op = project_api.client.data_transfer_api.get_metadata(storage_paths)
    op = project_api.client.data_transfer_api.wait_for(op.id)[0]
    log.info(f"Operation {op.state}")
    if op.state == OperationState.Succeeded:
        base_dir = project_api.project_id
        for f in files:
            if getattr(f, "src", None) is None:
                continue
            md = op.result[f"{base_dir}/{os.path.basename(f.storage_id)}"]
            f.hash = md["checksum"]
            f.size = md["size"]
    else:
        log.error("Failed to fetch metadata of uploaded files")
        raise HPSError("Failed to fetch metadata of uploaded files")


def create_files(project_api: ProjectApi, files, as_objects=True) -> list[File]:
    """Create a list of files."""
    # (1) Create file resources in JMS
    created_files = create_objects(
        project_api.client.session, project_api.url, files, File, as_objects=as_objects
    )

    # (2) Check if there are src properties, files to upload
    num_uploads = 0
    for f, cf in zip(files, created_files, strict=False):
        if getattr(f, "src", None) is not None:
            cf.src = f.src
            num_uploads += 1

    if num_uploads > 0:
        # (3) Upload file contents
        _upload_files(project_api, created_files)

        # (4) Update corresponding file resources in JMS with hashes of uploaded files
        created_files = update_objects(
            project_api.client.session, project_api.url, created_files, File, as_objects=as_objects
        )

    return created_files


def update_files(project_api: ProjectApi, files: list[File], as_objects=True) -> list[File]:
    """Update a list of files."""
    # Upload files first if there are any src parameters
    _upload_files(project_api, files)
    # Update file resources in JMS
    return update_objects(
        project_api.client.session, project_api.url, files, File, as_objects=as_objects
    )


def _download_file(
    project_api: ProjectApi,
    file: File,
    target_path: str,
    progress_handler: Callable[[int], None] = None,
) -> str:
    """Download a file."""
    project_api.client.initialize_data_transfer_client()

    if getattr(file, "hash", None) is None:
        log.warning(f"No hash found for file {file.name}.")

    download_path = os.path.join(target_path, file.evaluation_path)
    base_dir = project_api.project_id

    log.info(f"Downloading file {file.id}")
    src = StoragePath(path=f"{base_dir}/{os.path.basename(file.storage_id)}")
    dst = StoragePath(path=download_path, remote="local")

    if progress_handler is not None:
        progress_handler(0)

    op = project_api.client.data_transfer_api.copy([SrcDst(src=src, dst=dst)])
    op = project_api.client.data_transfer_api.wait_for([op.id])

    log.info(f"Operation {op[0].state}")

    if op[0].state != OperationState.Succeeded:
        log.error(f"Download of file {file.evaluation_path} with id {file.id} failed")
        return None

    if progress_handler is not None:
        progress_handler(file.size)

    return download_path


def copy_projects(
    project_api: ProjectApi, project_source_ids: list[str], wait: bool = True
) -> str | list[str]:
    """Copy projects."""
    return _copy_objects(
        project_api.client,
        project_api.jms_api_url,
        [Project(id=id) for id in project_source_ids],
        wait=wait,
    )


def archive_project(project_api: ProjectApi, target_path, include_job_files=True) -> str:
    """Archive projects."""
    # PUT archive request
    url = f"{project_api.url}/archive"
    query_params = {}
    if not include_job_files:
        query_params["download_files"] = "configuration"

    r = project_api.client.session.put(url, params=query_params)

    # Monitor archive operation
    operation_location = r.headers["location"]
    log.debug(f"Operation location: {operation_location}")
    operation_id = operation_location.rsplit("/", 1)[-1]

    op = project_api._jms_api.monitor_operation(operation_id)

    if not op.succeeded:
        raise HPSError(f"Failed to archive project {project_api.project_id}.\n{op}")

    download_link = op.result["backend_path"]

    # Download archive
    log.info(f"Project archive download link: {download_link}")

    if not os.path.isdir(target_path):
        raise HPSError(f"Project archive: target path does not exist {target_path}")

    file_path = os.path.join(target_path, download_link.rsplit("/")[-1])
    log.info(f"Download archive to {file_path}")

    _download_archive(project_api, download_link, file_path)

    log.info("Done saving project archive to disk.")
    return file_path


def _download_archive(project_api: ProjectApi, download_link, target_path):
    project_api.client.initialize_data_transfer_client()

    src = StoragePath(path=f"{download_link}")
    dst = StoragePath(path=target_path, remote="local")
    op = project_api.client.data_transfer_api.copy([SrcDst(src=src, dst=dst)])
    op = project_api.client.data_transfer_api.wait_for([op.id])

    log.info(f"Operation {op[0].state}")

    if op[0].state != OperationState.Succeeded:
        raise HPSError(f"Download of archive {download_link} failed")


def copy_jobs(project_api: ProjectApi, jobs: list[Job], as_objects=True, **query_params):
    """Create jobs by copying existing jobs."""
    ids = _copy_objects(client=project_api.client, api_url=project_api.url, objects=jobs, wait=True)
    return ids


def sync_jobs(project_api: ProjectApi, jobs: list[Job]):
    """Sync jobs."""
    url = f"{project_api.url}/jobs:sync"
    json_data = json.dumps({"job_ids": [obj.id for obj in jobs]})
    _ = project_api.client.session.put(f"{url}", data=json_data)
