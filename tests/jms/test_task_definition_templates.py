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

import json
import logging
import uuid

from marshmallow.utils import missing

from ansys.hps.client import HPSError
from ansys.hps.client.auth import AuthApi
from ansys.hps.client.jms import JmsApi
from ansys.hps.client.jms.resource import (
    HpcResources,
    Permission,
    TaskDefinitionTemplate,
    TemplateResourceRequirements,
)
from ansys.hps.client.jms.schema.task_definition_template import TaskDefinitionTemplateSchema
from tests.utils import create_new_user_client, delete_user

log = logging.getLogger(__name__)


def test_template_deserialization():

    json_data = {
        # "modification_time": "2021-09-16T12:27:44.771067+00:00",
        "creation_time": "2021-09-16T12:27:44.771067+00:00",
        "name": "Ansys Mechanical APDL 2021 R1 Default",
        "execution_command": """%executable% -b nolist -i %file:dat%
                                -o %file:out% -np %resource:num_cores%
                                -dis -s noread -p ansys""",
        "software_requirements": [
            {
                "name": "Ansys Mechanical APDL",
                "version": "21.1",
            }
        ],
        "input_files": [],
        "output_files": [
            {
                "name": "out",
                "evaluation_path": "solve.out",
                "type": "text/plain",
                "collect": True,
                "monitor": True,
            },
            {
                "name": "cnd",
                "evaluation_path": "file.cnd",
                "type": "application/octet-stream",
                "collect": True,
                "monitor": False,
            },
        ],
        "execution_context": {
            "parallel_processing_type": {
                "default": "DMP",
                "type": "string",
                "description": "Available parallel processing types.",
                "value_list": ["DMP", "SMP", "Hybrid"],
            },
        },
        "worker_context": {
            "max_runtime": 120,
            "max_num_parallel_tasks": 3,
        },
        "resource_requirements": {
            "hpc_resources": {
                "custom_orchestration_options": {
                    "sval": "value",
                    "bval": False,
                }
            }
        },
    }

    template = TaskDefinitionTemplateSchema().load(json_data)

    assert template.__class__.__name__ == "TaskDefinitionTemplate"
    assert template.modification_time == missing
    assert template.name == json_data["name"]
    assert template.execution_context["parallel_processing_type"].default == "DMP"
    assert len(template.execution_context["parallel_processing_type"].value_list) == 3
    assert "Hybrid" in template.execution_context["parallel_processing_type"].value_list
    assert len(template.output_files) == 2
    assert template.output_files[0].name == "out"
    assert template.output_files[1].type == "application/octet-stream"
    assert template.worker_context.max_num_parallel_tasks == 3
    assert template.worker_context.max_runtime == 120
    assert (
        template.resource_requirements.hpc_resources.custom_orchestration_options["sval"] == "value"
    )
    assert not template.resource_requirements.hpc_resources.custom_orchestration_options["bval"]

    json_data["software_requirements"][0]["version"] = "2022 R2"
    json_data["execution_command"] = "my command line"
    json_data["execution_context"] = {"my_new_field": {"default": "value", "type": "string"}}

    template = TaskDefinitionTemplateSchema().load(json_data)
    assert template.software_requirements[0].version == "2022 R2"
    assert template.execution_command == "my command line"
    assert template.execution_context["my_new_field"].default == "value"


def test_template_integration(client):

    jms_api = JmsApi(client)

    # Test get queries
    templates = jms_api.get_task_definition_templates()
    assert len(templates) > 0
    assert templates[0].id is not None

    templates = jms_api.get_task_definition_templates(as_objects=False)
    assert len(templates) > 0
    assert templates[0]["id"] is not None

    templates = jms_api.get_task_definition_templates(
        as_objects=False, fields=["name", "software_requirements"]
    )
    assert len(templates) > 0
    log.info(f"templates={json.dumps(templates, indent=4)}")
    if templates:
        assert "software_requirements" in templates[0].keys()
        assert "name" in templates[0]["software_requirements"][0].keys()
        assert "version" in templates[0]["software_requirements"][0].keys()

    templates = jms_api.get_task_definition_templates(fields=["name"])
    if templates:
        assert templates[0].software_requirements == missing

    # Create new template based on existing one
    template_name = f"new_template_{uuid.uuid4()}"
    templates = jms_api.get_task_definition_templates(limit=1)
    assert len(templates) == 1

    template = TaskDefinitionTemplate(
        name=template_name, software_requirements=templates[0].software_requirements
    )
    template.version = "1.0"
    templates = jms_api.create_task_definition_templates([template])
    assert len(templates) == 1
    template = templates[0]
    assert template.name == template_name

    # Modify template
    template.software_requirements[0].version = "2.0.1"
    template.resource_requirements = TemplateResourceRequirements(
        hpc_resources=HpcResources(num_gpus_per_node=2)
    )
    templates = jms_api.update_task_definition_templates([template])
    assert len(templates) == 1
    template = templates[0]
    assert template.software_requirements[0].version == "2.0.1"
    assert template.name == template_name
    assert template.resource_requirements.hpc_resources.num_gpus_per_node == 2

    # Delete template
    jms_api.delete_task_definition_templates([template])

    templates = jms_api.get_task_definition_templates(name=template_name)
    assert len(templates) == 0

    # Copy template
    templates = jms_api.get_task_definition_templates(limit=1)
    assert len(templates) == 1
    original_template = templates[0]
    new_template_id = jms_api.copy_task_definition_templates(templates)
    new_template = jms_api.get_task_definition_templates(id=new_template_id)[0]

    assert original_template.name in new_template.name
    assert original_template.version == new_template.version
    assert original_template.version == new_template.version
    assert (
        original_template.software_requirements[0].version
        == original_template.software_requirements[0].version
    )


def test_template_permissions(client, keycloak_client, is_admin):

    jms_api = JmsApi(client)

    templates = jms_api.get_task_definition_templates()

    # a regular deployment should have some default templates
    # with read all permissions + some user defined ones with
    # either user or group permissions
    for template in templates:
        permissions = jms_api.get_task_definition_template_permissions(template_id=template.id)
        for permission in permissions:
            assert permission.permission_type in ["organization", "user", "group", "anyone"]

    # create new template and check default permissions
    template = TaskDefinitionTemplate(name="my_template", version=uuid.uuid4())
    template = jms_api.create_task_definition_templates([template])[0]
    permissions = jms_api.get_task_definition_template_permissions(template_id=template.id)
    assert len(permissions) == 2
    assert permissions[0].permission_type == "user"
    assert permissions[0].role == "admin"
    assert permissions[0].value_id is not None
    assert permissions[1].permission_type == "organization"
    assert permissions[1].role == "reader"
    assert permissions[1].value_id == "onprem_account"

    # create test user
    user1, client1 = create_new_user_client(client.url, keycloak_client)
    jms_api1 = JmsApi(client1)

    # verify test user can't access the template
    client1_templates = jms_api1.get_task_definition_templates(id=template.id)
    assert len(client1_templates) == 0

    # grant read all permissions
    permissions.append(Permission(permission_type="anyone", role="reader", value_id=None))
    permissions = jms_api.update_task_definition_template_permissions(template.id, permissions)
    assert len(permissions) == 3

    # verify test user can now access the template
    client1_templates = jms_api1.get_task_definition_templates(id=template.id)
    assert len(client1_templates) == 1
    assert client1_templates[0].name == template.name

    # verify test user can't edit the template
    client1_templates[0].version = client1_templates[0].version + "-dev"

    except_obj = None
    try:
        client1_templates = jms_api1.update_task_definition_templates(client1_templates)
    except HPSError as e:
        except_obj = e
    assert except_obj.response.status_code == 403
    assert except_obj.description == "Access to this resource has been restricted"

    # grant write permissions to the user
    permissions.append(Permission(permission_type="user", role="writer", value_id=user1.id))
    permissions = jms_api.update_task_definition_template_permissions(template.id, permissions)
    assert len(permissions) == 4

    # verify test user can now edit the template
    client1_templates[0].version = client1_templates[0].version + "-dev"
    client1_templates = jms_api1.update_task_definition_templates(client1_templates)

    # Delete template
    jms_api.delete_task_definition_templates([template])

    # Let user1 create a template
    template = TaskDefinitionTemplate(name="my_template", version=uuid.uuid4())
    template = jms_api1.create_task_definition_templates([template])[0]
    template = jms_api1.get_task_definition_templates(id=template.id)[0]
    assert template.name == "my_template"
    permissions = jms_api1.get_task_definition_template_permissions(template_id=template.id)
    assert len(permissions) == 2
    assert permissions[0].permission_type == "user"
    assert permissions[0].role == "admin"
    assert permissions[0].value_id == user1.id
    assert permissions[1].permission_type == "organization"
    assert permissions[1].role == "reader"
    assert permissions[1].value_id == "onprem_account"

    # verify that an admin user can access the template
    if is_admin:
        admin_templates = jms_api.get_task_definition_templates(id=template.id)
        log.info(admin_templates)
        assert len(admin_templates) == 1
        assert admin_templates[0].name == template.name
        assert admin_templates[0].version == template.version

    # Delete template
    jms_api1.delete_task_definition_templates([template])

    # Delete user
    delete_user(keycloak_client, user1)


def test_template_permissions_update(client):

    jms_api = JmsApi(client)

    # create new template and check default permissions
    template = TaskDefinitionTemplate(name="my_template", version=uuid.uuid4())
    template = jms_api.create_task_definition_templates([template])[0]
    permissions = jms_api.get_task_definition_template_permissions(template_id=template.id)
    assert len(permissions) == 2
    assert permissions[0].permission_type == "user"
    assert permissions[1].permission_type == "organization"

    # change permissions
    permissions = [Permission(permission_type="anyone", role="admin", value_id=None)]
    permissions = jms_api.update_task_definition_template_permissions(
        template_id=template.id, permissions=permissions
    )
    assert len(permissions) == 1
    permissions = jms_api.get_task_definition_template_permissions(template_id=template.id)
    assert len(permissions) == 1
    assert permissions[0].permission_type == "anyone"

    # delete template
    jms_api.delete_task_definition_templates([template])


def test_template_anyone_permission(client, keycloak_client):

    jms_api = JmsApi(client)

    # create new template and check default permissions
    template = TaskDefinitionTemplate(name="my_template", version=uuid.uuid4())
    template = jms_api.create_task_definition_templates([template])[0]
    permissions = jms_api.get_task_definition_template_permissions(template_id=template.id)
    assert len(permissions) == 2
    assert permissions[0].permission_type == "user"
    assert permissions[0].role == "admin"
    assert permissions[0].value_id is not None
    assert permissions[1].permission_type == "organization"
    assert permissions[1].role == "reader"
    assert permissions[1].value_id == "onprem_account"

    # create test user
    user1, client1 = create_new_user_client(client.url, keycloak_client)
    jms_api1 = JmsApi(client1)

    # verify test user can't access the template
    client1_templates = jms_api1.get_task_definition_templates(id=template.id)
    assert len(client1_templates) == 0

    # grant read all permissions
    permissions.append(Permission(permission_type="anyone", role="reader", value_id=None))
    permissions = jms_api.update_task_definition_template_permissions(template.id, permissions)
    assert len(permissions) == 3

    # verify test user can now access the template
    client1_templates = jms_api1.get_task_definition_templates(id=template.id)
    assert len(client1_templates) == 1
    assert client1_templates[0].name == template.name

    # verify test user can't edit the template
    client1_templates[0].version = client1_templates[0].version + "-dev"

    except_obj = None
    try:
        client1_templates = jms_api1.update_task_definition_templates(client1_templates)
    except HPSError as e:
        except_obj = e
    assert except_obj.response.status_code == 403
    assert except_obj.description == "Access to this resource has been restricted"

    # grant write all permissions
    anyone_permission = next(p for p in permissions if p.permission_type == "anyone")
    anyone_permission.role = "writer"
    permissions = jms_api.update_task_definition_template_permissions(template.id, permissions)
    assert len(permissions) == 3
    for p in permissions:
        if p.permission_type == "anyone":
            assert p.role == "writer"

    # verify test user can now edit the template
    client1_templates = jms_api1.update_task_definition_templates(client1_templates)

    # Delete template
    jms_api.delete_task_definition_templates([template])

    # Delete user
    delete_user(keycloak_client, user1)


def test_template_delete(client, keycloak_client):

    auth_api = AuthApi(client)

    # create 2 non-admin users
    jms_api = JmsApi(client)
    user1, client1 = create_new_user_client(client.url, keycloak_client)
    assert not auth_api.user_is_admin(user1.id)
    jms_api1 = JmsApi(client1)
    user2, client2 = create_new_user_client(client.url, keycloak_client)
    assert not auth_api.user_is_admin(user2.id)
    jms_api2 = JmsApi(client2)

    # user1 creates new template
    template = TaskDefinitionTemplate(name="my_template", version=uuid.uuid4())
    template = jms_api1.create_task_definition_templates([template])[0]
    permissions = jms_api1.get_task_definition_template_permissions(template_id=template.id)
    assert len(permissions) == 2
    assert permissions[0].permission_type == "user"
    assert permissions[0].role == "admin"
    assert permissions[0].value_id == user1.id
    assert permissions[1].permission_type == "organization"
    assert permissions[1].role == "reader"
    assert permissions[1].value_id == "onprem_account"

    # verify user2 can't access the template
    client2_templates = jms_api2.get_task_definition_templates(id=template.id)
    assert len(client2_templates) == 0

    # user1 grants anyone read permissions
    permissions.append(Permission(permission_type="anyone", role="reader", value_id=None))
    permissions = jms_api1.update_task_definition_template_permissions(template.id, permissions)
    assert len(permissions) == 3

    # verify user2 can now access the template
    client2_templates = jms_api2.get_task_definition_templates(id=template.id)
    assert len(client2_templates) == 1
    assert client2_templates[0].name == template.name

    # verify user2 can't delete the template
    except_obj = None
    try:
        client2_templates = jms_api2.delete_task_definition_templates(client2_templates)
    except HPSError as e:
        except_obj = e
    assert except_obj is not None
    assert except_obj.response.status_code == 403
    assert except_obj.description == "Access to this resource has been restricted"

    # Delete the template
    jms_api1.delete_task_definition_templates([template])

    # Delete users
    delete_user(keycloak_client, user1)
    delete_user(keycloak_client, user2)
