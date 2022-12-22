import json
import logging
import os
from pathlib import Path
from typing import Callable, List

from cachetools import TTLCache, cached
from marshmallow.utils import missing
import requests

from ansys.rep.client.client import Client
from ansys.rep.client.common import Object
from ansys.rep.client.exceptions import ClientError, REPError
from ansys.rep.client.jms.resource import (
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
    TaskDefinition,
)
from ansys.rep.client.jms.schema.job import JobSchema

from .base import create_objects, delete_objects, get_objects, update_objects
from .jms_api import JmsApi, _monitor_operation, get_project

log = logging.getLogger(__name__)


class ProjectApi:
    """Exposes the Project endpoints of the Job Management Service

    Parameters
    ----------
    client : Client
        A REP client object.
    project_id : str
        ID of the project

    Examples
    --------

    >>> from ansys.rep.client import Client
    >>> from ansys.rep.client.jms import JmsApi, Project, ProjectApi
    >>> cl = Client(
    ...     rep_url="https://127.0.0.1:8443/rep", username="repadmin", password="repadmin"
    ... )
    >>> project = Project(name="Example Project")
    >>> print(project)
    {
        "name": "Example Project"
    }
    >>> jms_api = JmsApi(cl)
    >>> project = jms_api.create_project(project)
    >>> print(project)
    {
        "id": "02qtyJfpfAQ0fr3zkoIAfC",
        "name": "Example Project",
        "active": false,
        "priority": 1,
        "creation_time": ...
        ...
    }
    >>> project_api = ProjectApi(cl, project.id)
    >>> print(project_api)
    'https://127.0.0.1:8443/rep/jms/api/v1/projects/02qtyJfpfAQ0fr3zkoIAfC'
    >>> jobs = project_api.get_jobs()

    """

    def __init__(self, client: Client, project_id: str):
        self.client = client
        self.project_id = project_id
        self._fs_url = None
        self._fs_project_id = None

    @property
    def jms_api_url(self) -> str:
        return f"{self.client.rep_url}/jms/api/v1"

    @property
    def url(self) -> str:
        """Returns the API url"""
        return f"{self.jms_api_url}/projects/{self.project_id}"

    @property
    def fs_url(self) -> str:
        """URL of the file storage gateway"""
        if self._fs_url is None or self._fs_project_id != self.project_id:
            self._fs_project_id = self.project_id
            project = get_project(self.client, self.jms_api_url, id=self.project_id)
            self._fs_url = get_fs_url(project)
        return self._fs_url

    @property
    def fs_bucket_url(self) -> str:
        """URL of the project's bucket in the file storage gateway"""
        return f"{self.fs_url}/{self.project_id}"

    ################################################################
    # Project operations (copy, archive)
    def copy_project(self, project_target_name: str, wait: bool = True) -> str:
        """Duplicate project"""
        return copy_project(self, self.project_id, project_target_name, wait)

    def archive_project(self, path: str, include_job_files: bool = True):
        """Archive an existing project and save it to disk

        Args:
            path (str): Where to save the archive locally.
            include_job_files (bool, optional): Whether to include design point files in the
                                                archive. True by default.

        Returns:
            str: The path to the archive.
        """
        return archive_project(self, path, include_job_files)

    ################################################################
    # Files
    def get_files(self, as_objects=True, content=False, **query_params) -> List[File]:
        """
        Return a list of file resources, optionally filtered by given query parameters.
        If content=True, each files content is downloaded as well and stored in memory
        as :attr:`ansys.rep.client.jms.File.content`.
        """
        return get_files(self, as_objects=as_objects, content=content, **query_params)

    def create_files(self, files: List[File], as_objects=True) -> List[File]:
        return create_files(self, files, as_objects=as_objects)

    def update_files(self, files: List[File], as_objects=True):
        return update_files(self, files, as_objects=as_objects)

    def delete_files(self, files: List[File]):
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
    def get_parameter_definitions(
        self, as_objects=True, **query_params
    ) -> List[ParameterDefinition]:
        return self._get_objects(ParameterDefinition, as_objects, **query_params)

    def create_parameter_definitions(
        self, parameter_definitions, as_objects=True
    ) -> List[ParameterDefinition]:
        return self._create_objects(parameter_definitions, as_objects)

    def update_parameter_definitions(
        self, parameter_definitions: List[ParameterDefinition], as_objects=True
    ) -> List[ParameterDefinition]:
        return self._update_objects(parameter_definitions, as_objects)

    def delete_parameter_definitions(self, parameter_definitions: List[ParameterDefinition]):
        return self._delete_objects(parameter_definitions)

    ################################################################
    # Parameter mappings
    def get_parameter_mappings(self, as_objects=True, **query_params) -> List[ParameterMapping]:
        return self._get_objects(ParameterMapping, as_objects=as_objects, **query_params)

    def create_parameter_mappings(
        self, parameter_mappings: List[ParameterMapping], as_objects=True
    ) -> List[ParameterMapping]:
        return self._create_objects(parameter_mappings, as_objects=as_objects)

    def update_parameter_mappings(
        self, parameter_mappings: List[ParameterMapping], as_objects=True
    ) -> List[ParameterMapping]:
        return self._update_objects(parameter_mappings, as_objects=as_objects)

    def delete_parameter_mappings(self, parameter_mappings: List[ParameterMapping]):
        return self._delete_objects(parameter_mappings)

    ################################################################
    # Task definitions
    def get_task_definitions(self, as_objects=True, **query_params) -> List[TaskDefinition]:
        return self._get_objects(TaskDefinition, as_objects=as_objects, **query_params)

    def create_task_definitions(
        self, task_definitions: List[TaskDefinition], as_objects=True
    ) -> List[TaskDefinition]:
        return self._create_objects(task_definitions, as_objects=as_objects)

    def update_task_definitions(
        self, task_definitions: List[TaskDefinition], as_objects=True
    ) -> List[TaskDefinition]:
        return self._update_objects(task_definitions, as_objects=as_objects)

    def delete_task_definitions(self, task_definitions: List[TaskDefinition]):
        return self._delete_objects(task_definitions)

    ################################################################
    # Job definitions
    def get_job_definitions(self, as_objects=True, **query_params) -> List[JobDefinition]:
        return self._get_objects(JobDefinition, as_objects=as_objects, **query_params)

    def create_job_definitions(
        self, job_definitions: List[JobDefinition], as_objects=True
    ) -> List[JobDefinition]:
        return self._create_objects(job_definitions, as_objects=as_objects)

    def update_job_definitions(
        self, job_definitions: List[JobDefinition], as_objects=True
    ) -> List[JobDefinition]:
        return self._update_objects(job_definitions, as_objects=as_objects)

    def delete_job_definitions(self, job_definitions: List[JobDefinition]):
        return self._delete_objects(job_definitions)

    ################################################################
    # Jobs
    def get_jobs(self, as_objects=True, **query_params) -> List[Job]:
        return self._get_objects(Job, as_objects=as_objects, **query_params)

    def create_jobs(self, jobs: List[Job], as_objects=True) -> List[Job]:
        """Create new jobs

        Args:
            jobs (list of :class:`ansys.rep.client.jms.Job`): A list of Job objects
            as_objects (bool): Whether to return jobs as objects or dictionaries

        Returns:
            List of :class:`ansys.rep.client.jms.Job` or list of dict if `as_objects` is False
        """
        return self._create_objects(jobs, as_objects=as_objects)

    def copy_jobs(self, jobs: List[Job], as_objects=True, **query_params):
        """Create new jobs by copying existing ones

        Args:
            jobs (list of :class:`ansys.rep.client.jms.Job`): A list of job objects

        Note that only the ``id`` field of the Job objects need to be filled;
        the other fields can be empty.
        """
        return copy_jobs(self, jobs, as_objects=as_objects, **query_params)

    def update_jobs(self, jobs: List[Job], as_objects=True) -> List[Job]:
        """Update existing jobs

        Args:
            jobs (list of :class:`ansys.rep.client.jms.Job`): A list of job objects
            as_objects (bool): Whether to return jobs as objects or dictionaries

        Returns:
            List of :class:`ansys.rep.client.jms.Job` or list of dict if `as_objects` is True
        """
        return self._update_objects(jobs, as_objects=as_objects)

    def delete_jobs(self, jobs: List[Job]):
        """Delete existing jobs

        Args:
            jobs (list of :class:`ansys.rep.client.jms.Job`): A list of Job objects

        Note that only the ``id`` field of the Job objects need to be filled;
        the other fields can be empty.

        Example:

            >>> jobs_to_delete = []
            >>> for id in [1,2,39,44]:
            >>>    jobs_to_delete.append(Job(id=id))
            >>> project_api.delete_jobs(jobs_to_delete)

        """
        return self._delete_objects(jobs)

    def _sync_jobs(self, jobs: List[Job]):
        log.warning("ProjectApi._sync_jobs is a beta feature. Use with care.")
        return sync_jobs(self, jobs)

    ################################################################
    # Tasks
    def get_tasks(self, as_objects=True, **query_params) -> List[Task]:
        return self._get_objects(Task, as_objects=as_objects, **query_params)

    def update_tasks(self, tasks: List[Task], as_objects=True) -> List[Task]:
        return self._update_objects(tasks, as_objects=as_objects)

    ################################################################
    # Selections
    def get_job_selections(self, as_objects=True, **query_params) -> List[JobSelection]:
        return self._get_objects(JobSelection, as_objects=as_objects, **query_params)

    def create_job_selections(
        self, selections: List[JobSelection], as_objects=True
    ) -> List[JobSelection]:
        return self._create_objects(selections, as_objects=as_objects)

    def update_job_selections(
        self, selections: List[JobSelection], as_objects=True
    ) -> List[JobSelection]:
        return self._update_objects(selections, as_objects=as_objects)

    def delete_job_selections(self, selections: List[JobSelection]):
        return self._delete_objects(selections)

    ################################################################
    # Algorithms
    def get_algorithms(self, as_objects=True, **query_params) -> List[Algorithm]:
        return self._get_objects(Algorithm, as_objects=as_objects, **query_params)

    def create_algorithms(self, algorithms: List[Algorithm], as_objects=True) -> List[Algorithm]:
        return self._create_objects(algorithms, as_objects=as_objects)

    def update_algorithms(self, algorithms: List[Algorithm], as_objects=True) -> List[Algorithm]:
        return self._update_objects(algorithms, as_objects=as_objects)

    def delete_algorithms(self, algorithms: List[Algorithm]):
        return self._delete_objects(algorithms)

    ################################################################
    # Permissions
    def get_permissions(self, as_objects=True) -> List[Permission]:
        return self._get_objects(Permission, as_objects=as_objects, fields=None)

    def update_permissions(self, permissions: List[Permission], as_objects=True):
        return self._update_objects(permissions, as_objects=as_objects)

    ################################################################
    # License contexts
    def get_license_contexts(self, as_objects=True, **query_params) -> List[LicenseContext]:
        return self._get_objects(self, LicenseContext, as_objects=as_objects, **query_params)

    def create_license_contexts(self, as_objects=True) -> List[LicenseContext]:
        rest_name = LicenseContext.Meta.rest_name
        url = f"{self.jms_api_url}/projects/{self.project_id}/{rest_name}"
        r = self.client.session.post(f"{url}")
        data = r.json()[rest_name]
        if not as_objects:
            return data
        schema = LicenseContext.Meta.schema(many=True)
        objects = schema.load(data)
        return objects

    def update_license_contexts(self, license_contexts, as_objects=True) -> List[LicenseContext]:
        return self._update_objects(self, license_contexts, as_objects=as_objects)

    def delete_license_contexts(self):
        rest_name = LicenseContext.Meta.rest_name
        url = f"{self.jms_api_url}/projects/{self.id}/{rest_name}"
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
    # (1) Create file resources in JMS
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

        # (4) Update corresponding file resources in JMS with hashes of uploaded files
        created_files = update_objects(
            project_api.client.session, project_api.url, created_files, as_objects=as_objects
        )

    return created_files


def update_files(project_api: ProjectApi, files: List[File], as_objects=True) -> List[File]:
    # Upload files first if there are any src parameters
    _upload_files(project_api, files)
    # Update file resources in JMS
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


def copy_project(project_api: ProjectApi, project_source_id, project_target_name, wait=True) -> str:

    url = f"{project_api.url}/copy"
    r = project_api.client.session.put(url, params={"project_name": project_target_name})

    operation_location = r.headers["location"]
    operation_id = operation_location.rsplit("/", 1)[-1]

    if not wait:
        return operation_location

    op = _monitor_operation(JmsApi(project_api.client), operation_id, 1.0)
    if not op.succeeded:
        raise REPError(f"Failed to copy project {project_source_id}.")
    return op.result["project_id"]


def archive_project(project_api: ProjectApi, target_path, include_job_files=True) -> str:

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

    op = _monitor_operation(JmsApi(project_api.client), operation_id, 1.0)

    if not op.succeeded:
        raise REPError(f"Failed to archive project {project_api.project_id}.\n{op}")

    download_link = op.result["backend_path"]

    # Download archive
    download_link = download_link.replace("ansfs://", project_api.fs_url + "/")
    log.info(f"Project archive download link: {download_link}")

    if not os.path.isdir(target_path):
        raise REPError(f"Project archive: target path does not exist {target_path}")

    file_path = os.path.join(target_path, download_link.rsplit("/")[-1])
    log.info(f"Download archive to {file_path}")

    with project_api.client.session.get(download_link, stream=True) as r:
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    log.info(f"Done saving project archive to disk")
    return file_path


def copy_jobs(project_api: ProjectApi, jobs: List[Job], as_objects=True, **query_params):
    """Create new jobs by copying existing ones"""

    url = f"{project_api.url}/jobs"

    query_params.setdefault("fields", "all")

    json_data = json.dumps({"source_ids": [obj.id for obj in jobs]})
    r = project_api.client.session.post(f"{url}", data=json_data, params=query_params)

    data = r.json()["jobs"]
    if not as_objects:
        return data

    return JobSchema(many=True).load(data)


def sync_jobs(project_api: ProjectApi, jobs: List[Job]):

    url = f"{project_api.url}/jobs:sync"
    json_data = json.dumps({"job_ids": [obj.id for obj in jobs]})
    r = project_api.client.session.put(f"{url}", data=json_data)


@cached(cache=TTLCache(1024, 60), key=lambda project: project.id)
def get_fs_url(project: Project):
    if project.file_storages == missing:
        raise REPError(f"The project object has no file storages information.")
    rest_gateways = [fs for fs in project.file_storages if fs["obj_type"] == "RestGateway"]
    rest_gateways.sort(key=lambda fs: fs["priority"], reverse=True)

    # Local deployments use "https://host.docker.internal:8443/rep/fs/api" as first
    # FS Rest Gateway address and "https://localhost:8443/rep/fs/api/" only as second.
    # host.docker.internal is only available from within Docker, causing the first ping
    # further down to always fail, with a time penalty of 2 seconds. This is particularly
    # annoying when running tests.
    # Therefore, we try to detect such case and move the host.docker.internal entry
    # to the bottom of the list.
    docker_index = next(
        (i for i, rg in enumerate(rest_gateways) if "host.docker.internal" in rg["url"]), None
    )
    if docker_index is not None:
        rest_gateways.append(rest_gateways.pop(docker_index))

    if not rest_gateways:
        raise REPError(f"Project {project.name} (id={project.id}) has no Rest Gateway defined.")

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
