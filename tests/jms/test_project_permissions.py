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

import logging
import time
import uuid

from ansys.hps.client import Client
from ansys.hps.client.auth import AuthApi, User
from ansys.hps.client.exceptions import ClientError
from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import JobDefinition, Permission, Project
from tests.utils import create_user, delete_user

log = logging.getLogger(__name__)


def add_job_definition_to_project(project_api: ProjectApi, config_name):
    log.info(f"=== Add job_definition {config_name} to project {project_api.project_id}")
    job_def = JobDefinition(name=config_name, active=True)
    project_api.create_job_definitions([job_def])


def grant_permissions(project_api: ProjectApi, user):
    log.info(f"=== Granting permissions to {user.username}")
    permissions = project_api.get_permissions()
    log.info(f"Permissions before: {permissions}")
    permissions.append(
        Permission(
            permission_type="user", value_name=user.username, role="writer", value_id=user.id
        )
    )
    permissions = project_api.update_permissions(permissions)
    log.info(f"Permissions after: {permissions}")


def remove_permissions(project_api: ProjectApi, user):
    log.info(f"=== Removing permissions to {user.username}")
    permissions = project_api.get_permissions()
    log.info(f"Permissions before: {permissions}")
    permissions = [p for p in permissions if p.value_name != user.username]
    permissions = project_api.update_permissions(permissions)
    log.info(f"Permissions after: {permissions}")


def test_get_project_permissions(client):
    jms_api = JmsApi(client)
    proj_name = "test_jms_get_permissions_test"

    proj = Project(name=proj_name, active=True, priority=10)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    perms = [p for p in project_api.get_permissions() if p.permission_type == "user"]
    assert len(perms) == 1
    assert perms[0].value_name == client.username
    assert perms[0].role == "admin"
    assert perms[0].permission_type == "user"

    # Delete project
    jms_api.delete_project(proj)


def test_modify_project_permissions(client, keycloak_client):
    user_credentials = {
        "user1": {"username": f"testuser-{uuid.uuid4().hex[:8]}", "password": "test"},
        "user2": {"username": f"testuser-{uuid.uuid4().hex[:8]}", "password": "test"},
    }
    proj_name = f"test_jms_get_permissions_test_{uuid.uuid4().hex[:8]}"

    auth_api = AuthApi(client)
    existing_users = [u.username for u in auth_api.get_users()]

    if user_credentials["user1"]["username"] not in existing_users:
        user1 = create_user(
            keycloak_client,
            User(
                username=user_credentials["user1"]["username"],
                password=user_credentials["user1"]["password"],
            ),
        )
    else:
        user1 = [
            u for u in auth_api.get_users() if u.username == user_credentials["user1"]["username"]
        ][0]

    log.info(f"User 1: {user1}")

    if user_credentials["user2"]["username"] not in existing_users:
        user2 = create_user(
            keycloak_client,
            User(
                username=user_credentials["user2"]["username"],
                password=user_credentials["user2"]["password"],
            ),
        )
    else:
        user2 = [
            u for u in auth_api.get_users() if u.username == user_credentials["user2"]["username"]
        ][0]

    log.info(f"User 2: {user2}")

    # user1 creates a project and a job definition
    client1 = Client(
        url=client.url,
        username=user1.username,
        password=user_credentials["user1"]["password"],
    )
    log.info(f"Client connected at {client1.url} with user {user1.username}")

    root_api1 = JmsApi(client1)
    proj = Project(name=proj_name, priority=1, active=True)
    proj = root_api1.create_project(proj, replace=True)
    project_api = ProjectApi(client1, proj.id)
    log.info(f"Created new project with id={proj.id}")

    add_job_definition_to_project(project_api, f"Config 1 - {user1.username}")
    assert len(project_api.get_job_definitions()) == 1

    # user1 shares the project with user2
    grant_permissions(project_api, user2)
    permissions = [p for p in project_api.get_permissions() if p.permission_type == "user"]
    assert len(permissions) == 2
    assert user1.username in [x.value_name for x in permissions]
    assert user2.username in [x.value_name for x in permissions]

    # user1 appends a job definition to the project
    client2 = Client(
        url=client.url,
        username=user2.username,
        password=user_credentials["user2"]["password"],
    )
    root_api2 = JmsApi(client2)
    log.info(f"Client connected at {client2.url} with user {user2.username}")

    proj_user2 = root_api2.get_project(id=proj.id)
    project_api2 = ProjectApi(client2, proj_user2.id)
    add_job_definition_to_project(project_api2, f"Config 2 - {user2.username}")

    assert len(project_api2.get_job_definitions()) == 2

    # user1 removes permissions to user2
    remove_permissions(project_api, user2)
    permissions = [p for p in project_api.get_permissions() if p.permission_type == "user"]
    assert len(permissions) == 1
    assert user1.username in [x.value_name for x in permissions]
    assert user2.username not in [x.value_name for x in permissions]

    # user2 reconnects and tries to get the project
    client2 = Client(
        url=client.url,
        username=user2.username,
        password=user_credentials["user2"]["password"],
    )
    root_api2 = JmsApi(client2)
    time.sleep(5)

    # this should return 403 forbidden by now, instead it returns an empty response
    except_obj = None
    try:
        proj_user2 = root_api2.get_project(id=proj_user2.id)
    except ClientError as e:
        except_obj = e
        log.error(str(e))

    assert except_obj is not None
    assert except_obj.response.status_code, 403

    root_api1.delete_project(proj)
    delete_user(keycloak_client, user1)
    delete_user(keycloak_client, user2)
