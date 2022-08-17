import logging
import os
from pathlib import Path
from typing import Callable, List

from ansys.rep.client.exceptions import ClientError

from ..client import Client
from ..resource.algorithm import Algorithm
from ..resource.base import Object
from ..resource.file import File
from ..resource.job import Job, copy_jobs, sync_jobs
from ..resource.job_definition import JobDefinition
from ..resource.license_context import LicenseContext
from ..resource.parameter_definition import ParameterDefinition
from ..resource.parameter_mapping import ParameterMapping
from ..resource.project import get_fs_url, get_project
from ..resource.project_permission import ProjectPermission, update_permissions
from ..resource.selection import Selection
from ..resource.task import Task
from ..resource.task_definition import TaskDefinition
from .base import create_objects, delete_objects, get_objects, update_objects

log = logging.getLogger(__name__)


class ProjectApi:
    """Project API

    Args:
        client (:class:`ansys.rep.client.jms.Client`): A client object.
        project_id (str):

    Example:

        >>> project = Project(name="Example Project")
        >>> project = client.create_project(project)
        >>> project_api = ProjectApi(client, project.id)
        >>> jobs = project_api.get_jobs()

    """

    def __init__(self, client: Client, project_id: str):
        self.client = client
        self.project_id = project_id

    @property
    def url(self):
        return f"{self.client.jms_api_url}/projects/{self.project_id}"

    @property
    def fs_url(self):
        """URL of the file storage gateway"""
        project = get_project(self.client, id=self.project_id)
        return get_fs_url(project)

    @property
    def fs_bucket_url(self):
        """URL of the project's bucket in the file storage gateway"""
        return f"{self.fs_url}/{self.project_id}"

    ################################################################
    # Files
    def get_files(self, as_objects=True, content=False, **query_params):
        """
        Return a list of file resources, optionally filtered by given query parameters.
        If content=True, each files content is downloaded as well and stored in memory
        as :attr:`ansys.rep.client.jms.File.content`.
        """
        return get_files(self, as_objects=as_objects, content=content, **query_params)

    def create_files(self, files, as_objects=True):
        return create_files(self, files, as_objects=as_objects)

    def update_files(self, files, as_objects=True):
        return update_files(self, files, as_objects=as_objects)

    def delete_files(self, files):
        return self._delete_objects(files)

    def download_file(
        self,
        file: File,
        target_path: str,
        stream: bool = True,
        progress_handler: Callable[[int], None] = None,
    ) -> str:
        """
        Download file content and save it to disk. If stream=True,
        data is retrieved in chunks, avoiding storing the entire content
        in memory.
        """
        return _download_file(self, file, target_path, progress_handler, stream)

    ################################################################
    # Parameter definitions
    def get_parameter_definitions(self, as_objects=True, **query_params):
        return self._get_objects(ParameterDefinition, as_objects, **query_params)

    def create_parameter_definitions(self, parameter_definitions, as_objects=True):
        return self._create_objects(parameter_definitions, as_objects)

    def update_parameter_definitions(self, parameter_definitions, as_objects=True):
        return self._update_objects(parameter_definitions, as_objects)

    def delete_parameter_definitions(self, parameter_definitions):
        return self._delete_objects(parameter_definitions)

    ################################################################
    # Parameter mappings
    def get_parameter_mappings(self, as_objects=True, **query_params):
        return self._get_objects(ParameterMapping, as_objects=as_objects, **query_params)

    def create_parameter_mappings(self, parameter_mappings, as_objects=True):
        return self._create_objects(parameter_mappings, as_objects=as_objects)

    def update_parameter_mappings(self, parameter_mappings, as_objects=True):
        return self._update_objects(parameter_mappings, as_objects=as_objects)

    def delete_parameter_mappings(self, parameter_mappings):
        return self._delete_objects(parameter_mappings)

    ################################################################
    # Task definitions
    def get_task_definitions(self, as_objects=True, **query_params):
        return self._get_objects(TaskDefinition, as_objects=as_objects, **query_params)

    def create_task_definitions(self, task_definitions, as_objects=True):
        return self._create_objects(task_definitions, as_objects=as_objects)

    def update_task_definitions(self, task_definitions, as_objects=True):
        return self._update_objects(task_definitions, as_objects=as_objects)

    def delete_task_definitions(self, task_definitions):
        return self._delete_objects(task_definitions)

    ################################################################
    # Job definitions
    def get_job_definitions(self, as_objects=True, **query_params):
        return self._get_objects(JobDefinition, as_objects=as_objects, **query_params)

    def create_job_definitions(self, job_definitions, as_objects=True):
        return self._create_objects(job_definitions, as_objects=as_objects)

    def update_job_definitions(self, job_definitions, as_objects=True):
        return self._update_objects(job_definitions, as_objects=as_objects)

    def delete_job_definitions(self, job_definitions):
        return self._delete_objects(job_definitions)

    ################################################################
    # Jobs
    def get_jobs(self, as_objects=True, **query_params):
        return self._get_objects(Job, as_objects=as_objects, **query_params)

    def create_jobs(self, jobs, as_objects=True):
        """Create new jobs

        Args:
            jobs (list of :class:`ansys.rep.client.jms.Job`): A list of Job objects
            as_objects (bool): Whether to return jobs as objects or dictionaries

        Returns:
            List of :class:`ansys.rep.client.jms.Job` or list of dict if `as_objects` is False
        """
        return self._create_objects(jobs, as_objects=as_objects)

    def copy_jobs(self, jobs, as_objects=True):
        """Create new jobs by copying existing ones

        Args:
            jobs (list of :class:`ansys.rep.client.jms.Job`): A list of job objects

        Note that only the ``id`` field of the Job objects need to be filled;
        the other fields can be empty.
        """
        return copy_jobs(self, jobs, as_objects=as_objects)

    def update_jobs(self, jobs, as_objects=True):
        """Update existing jobs

        Args:
            jobs (list of :class:`ansys.rep.client.jms.Job`): A list of job objects
            as_objects (bool): Whether to return jobs as objects or dictionaries

        Returns:
            List of :class:`ansys.rep.client.jms.Job` or list of dict if `as_objects` is True
        """
        return self._update_objects(jobs, as_objects=as_objects)

    def delete_jobs(self, jobs):
        """Delete existing jobs

        Args:
            jobs (list of :class:`ansys.rep.client.jms.Job`): A list of Job objects

        Note that only the ``id`` field of the Job objects need to be filled;
        the other fields can be empty.

        Example:

            >>> dps_to_delete = []
            >>> for id in [1,2,39,44]:
            >>>    dps_to_delete.append(Job(id=id))
            >>> project_api.delete_jobs(dps_to_delete)

        """
        return self._delete_objects(jobs)

    def _sync_jobs(self, jobs):
        return sync_jobs(self, jobs)

    ################################################################
    # Tasks
    def get_tasks(self, as_objects=True, **query_params):
        return self._get_objects(Task, as_objects=as_objects, **query_params)

    def update_tasks(self, tasks, as_objects=True):
        return self._update_objects(tasks, as_objects=as_objects)

    ################################################################
    # Selections
    def get_selections(self, as_objects=True, **query_params):
        return self._get_objects(Selection, as_objects=as_objects, **query_params)

    def create_selections(self, selections, as_objects=True):
        return self._create_objects(self, selections, as_objects=as_objects)

    def update_selections(self, selections, as_objects=True):
        return self._update_objects(selections, as_objects=as_objects)

    def delete_selections(self, selections):
        return self._delete_objects(self, selections)

    ################################################################
    # Algorithms
    def get_algorithms(self, as_objects=True, **query_params):
        return self._get_objects(self, Algorithm, as_objects=as_objects, **query_params)

    def create_algorithms(self, algorithms, as_objects=True):
        return self._create_objects(self, algorithms, as_objects=as_objects)

    def update_algorithms(self, algorithms, as_objects=True):
        return self._update_objects(self, algorithms, as_objects=as_objects)

    def delete_algorithms(self, algorithms):
        return self._delete_objects(self, algorithms)

    ################################################################
    # Permissions
    def get_permissions(self, as_objects=True):
        return self._get_objects(self, ProjectPermission, as_objects=as_objects)

    def update_permissions(self, permissions):
        # the rest api currently doesn't return anything on permissions update
        update_permissions(self, permissions)

    ################################################################
    # License contexts
    def get_license_contexts(self, as_objects=True, **query_params):
        return self._get_objects(self, LicenseContext, as_objects=as_objects, **query_params)

    def create_license_contexts(self, as_objects=True):
        rest_name = LicenseContext.Meta.rest_name
        url = f"{self.client.jms_api_url}/projects/{self.id}/{rest_name}"
        r = self.client.session.post(f"{url}")
        data = r.json()[rest_name]
        if not as_objects:
            return data
        schema = LicenseContext.Meta.schema(many=True)
        objects = schema.load(data)
        return objects

    def update_license_contexts(self, license_contexts, as_objects=True):
        return self._update_objects(self, license_contexts, as_objects=as_objects)

    def delete_license_contexts(self):
        rest_name = LicenseContext.Meta.rest_name
        url = f"{self.client.jms_api_url}/projects/{self.id}/{rest_name}"
        r = self.client.session.delete(url)

    ################################################################
    def _get_objects(self, obj_type: Object, as_objects=True, **query_params):
        return get_objects(self.client.session, self.url, obj_type, as_objects, **query_params)

    def _create_objects(self, objects: List[Object], as_objects=True, **query_params):
        return create_objects(self.client.session, self.url, objects, as_objects, **query_params)

    def _update_objects(self, objects: List[Object], as_objects=True, **query_params):
        return update_objects(self.client.session, self.url, objects, as_objects, **query_params)

    def _delete_objects(self, objects: List[Object]):
        delete_objects(self.client.session, self.url, objects)


def _download_files(project_api: ProjectApi, files: List[File]):
    """
    Temporary implementation of file download directly using fs REST gateway.
    To be replaced with direct ansft calls, when it is available as python pkg
    """

    for f in files:
        if getattr(f, "hash", None) is not None:
            r = project_api.client.session.get(f"{project_api.fs_bucket_url}/{f.storage_id}")
            f.content = r.content
            f.content_type = r.headers["Content-Type"]


def get_files(project_api: ProjectApi, as_objects=True, content=False, **query_params):

    files = get_objects(
        project_api.client.session, project_api.url, File, as_objects=as_objects, **query_params
    )
    if content:
        _download_files(project_api, files)
    return files


def _upload_files(project_api: ProjectApi, files):
    """
    Temporary implementation of file upload directly using fs REST gateway.
    To be replaced with direct ansft calls, when it is available as python pkg
    """
    fs_headers = {"content-type": "application/octet-stream"}

    for f in files:
        if getattr(f, "src", None) is not None:
            with open(f.src, "rb") as file_content:
                r = project_api.client.session.post(
                    f"{project_api.fs_bucket_url}/{f.storage_id}",
                    data=file_content,
                    headers=fs_headers,
                )
                f.hash = r.json()["checksum"]
                f.size = os.path.getsize(f.src)


def create_files(project_api: ProjectApi, files, as_objects=True) -> List[File]:
    # (1) Create file resources in DPS
    created_files = create_objects(
        project_api.client.session, project_api.url, files, as_objects=as_objects
    )

    # (2) Check if there are src properties, files to upload
    num_uploads = 0
    for f, cf in zip(files, created_files):
        if getattr(f, "src", None) is not None:
            cf.src = f.src
            num_uploads += 1

    if num_uploads > 0:

        # (3) Upload file contents
        _upload_files(project_api, created_files)

        # (4) Update corresponding file resources in DPS with hashes of uploaded files
        created_files = update_objects(
            project_api.client.session, project_api.url, created_files, as_objects=as_objects
        )

    return created_files


def update_files(project_api: ProjectApi, files: List[File], as_objects=True) -> List[File]:
    # Upload files first if there are any src parameters
    _upload_files(project_api, files)
    # Update file resources in DPS
    return update_objects(project_api.client.session, project_api.url, files, as_objects=as_objects)


def _download_file(
    project_api: ProjectApi,
    file: File,
    target_path: str,
    progress_handler: Callable[[int], None] = None,
    stream: bool = True,
) -> str:

    if getattr(file, "hash", None) is None:
        raise ClientError(f"No hash found. Failed to download file {file.name}")

    Path(target_path).mkdir(parents=True, exist_ok=True)
    download_link = f"{project_api.fs_bucket_url}/{file.storage_id}"
    download_path = os.path.join(target_path, file.evaluation_path)

    with project_api.client.session.get(download_link, stream=stream) as r, open(
        download_path, "wb"
    ) as f:
        for chunk in r.iter_content(chunk_size=None):
            f.write(chunk)
            if progress_handler is not None:
                progress_handler(len(chunk))

    return download_path
