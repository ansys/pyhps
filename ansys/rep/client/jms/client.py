# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri, O.Koenig
# ----------------------------------------------------------

from ..auth import authenticate
from ..connection import create_session
from ..exceptions import raise_for_status
from .resource.evaluator import get_evaluators, update_evaluators
from .resource.project import (
    archive_project,
    copy_project,
    create_project,
    delete_project,
    get_project,
    get_projects,
    restore_project,
    update_project,
)
from .resource.task_definition_template import (
    create_task_definition_templates,
    delete_task_definition_templates,
    get_task_definition_templates,
    update_task_definition_templates,
)


class Client(object):
    """A python interface to the Design Point Service API.

    Uses the provided credentials to create and store
    an authorized :class:`requests.Session` object.

    The following authentication workflows are supported:

        - Username and password: the client connects to the OAuth server and
          requests access and refresh tokens.
        - Refresh token: the client connects to the OAuth server and
          requests a new access token.
        - Access token: no authentication needed.

    Args:
        rep_url (str): The base path for the server to call,
                       e.g. "https://127.0.0.1/dcs".
        username (str): Username (Optional)
        password (str): Password (Optional)
        refresh_token (str): Refresh Token (Optional)
        access_token (str): Access Token (Optional)

    Example:

        >>> from ansys.rep.client.jms import Client
        >>> # Create client object and connect to DCS with username & password
        >>> cl = Client(rep_url="https://127.0.0.1/dcs", username="dcadmin", password="dcadmin")
        >>> # Extract refresh token to eventually store it
        >>> refresh_token = cl.refresh_token
        >>> # Alternative: Create client object and connect to DCS with refresh token
        >>> cl = Client(rep_url="https://127.0.0.1/dcs", refresh_token=refresh_token)

    """

    def __init__(
        self,
        rep_url: str = "https://127.0.0.1:8443/rep",
        username: str = "repadmin",
        password: str = "repadmin",
        *,
        realm: str = "rep",
        grant_type: str = "password",
        scope="openid",
        client_id: str = "rep-cli",
        client_secret: str = None,
        access_token: str = None,
        refresh_token: str = None,
        auth_url: str = None,
    ):

        self.rep_url = rep_url
        self.jms_api_url = self.rep_url + "/jms/api/v1"
        self.auth_url = auth_url
        self.refresh_token = None

        if access_token:
            self.access_token = access_token
        else:
            tokens = authenticate(
                url=auth_url or rep_url,
                realm=realm,
                grant_type=grant_type,
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                refresh_token=refresh_token,
            )
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]

        self.session = create_session(self.access_token)
        # register hook to handle expiring of the refresh token
        self.session.hooks["response"] = [self._auto_refresh_token, raise_for_status]
        self.unauthorized_num_retry = 0
        self._unauthorized_max_retry = 1

    def _auto_refresh_token(self, response, *args, **kwargs):
        """Hook function to automatically refresh the access token and
        re-send the request in case of unauthorized error"""
        if (
            response.status_code == 401
            and self.unauthorized_num_retry < self._unauthorized_max_retry
        ):
            self.unauthorized_num_retry += 1
            self.refresh_access_token()
            response.request.headers.update(
                {"Authorization": self.session.headers["Authorization"]}
            )
            return self.session.send(response.request)

        self.unauthorized_num_retry = 0
        return response

    def refresh_access_token(self):
        """Use the refresh token to obtain a new access token"""
        tokens = authenticate(url=self.auth_url or self.rep_url, refresh_token=self.refresh_token)
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        self.session.headers.update({"Authorization": "Bearer %s" % tokens["access_token"]})

    def get_api_info(self):
        """Return info like version, build date etc of the DPS API the client is connected to"""
        r = self.session.get(self.jms_api_url)
        return r.json()

    def get_projects(self, **query_params):
        """Return a list of projects, optionally filtered by given query parameters"""
        return get_projects(self, **query_params)

    def get_project(self, id=None, name=None):
        """Return a single project for given project id"""
        return get_project(self, id, name)

    def create_project(self, project, replace=False, as_objects=True):
        """Create a new project"""
        return create_project(self, project, replace, as_objects)

    def update_project(self, project, as_objects=True):
        """Update an existing project"""
        return update_project(self, project, as_objects)

    def delete_project(self, project):
        """Delete a project"""
        return delete_project(self, project)

    def copy_project(self, project, project_target_name):
        """Copy an existing project"""
        return copy_project(self, project.id, project_target_name)

    def archive_project(self, project, path, include_job_files=True):
        """Archive an existing project and save it to disk

        Args:
            project (:class:`ansys.rep.client.jms.Project`): A Project object
                                                            (only the id field is needed).
            path (str): Where to save the archive locally.
            include_job_files (bool, optional): Whether to include design point files in the
                                                archive. True by default.

        Returns:
            str: The path to the archive.
        """
        return archive_project(self, project, path, include_job_files)

    def restore_project(self, path, project_name):
        """Restore a project from an archive

        Args:
            path (str): Path of the archive file to be restored.
            project_id (str): ID of the restored project.

        Returns:
            :class:`ansys.rep.client.jms.Project`: A Project object.
        """
        return restore_project(self, path, project_name)

    def get_evaluators(self, as_objects=True, **query_params):
        """Return a list of evaluators, optionally filtered by given query parameters"""
        return get_evaluators(self, as_objects=as_objects, **query_params)

    def update_evaluators(self, evaluators, as_objects=True):
        """Update evaluators job_definition"""
        return update_evaluators(self, evaluators, as_objects=as_objects)

    def get_task_definition_templates(self, as_objects=True, **query_params):
        """Return a list of task definition templates,
        optionally filtered by given query parameters"""
        return get_task_definition_templates(self, as_objects=as_objects, **query_params)

    def create_task_definition_templates(self, templates):
        """Create new task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return create_task_definition_templates(self, templates)

    def update_task_definition_templates(self, templates):
        """Update existing task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return update_task_definition_templates(self, templates)

    def delete_task_definition_templates(self, templates):
        """Delete existing task definition templates

        Args:
            templates (list of :class:`ansys.rep.client.jms.TaskDefinitionTemplate`):
                A list of task definition templates
        """
        return delete_task_definition_templates(self, templates)
