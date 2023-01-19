# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import json
import logging
import unittest
import uuid

from marshmallow.utils import missing

from ansys.rep.client import Client, REPError
from ansys.rep.client.auth import AuthApi, User
from ansys.rep.client.jms import JmsApi
from ansys.rep.client.jms.resource import Permission, TaskDefinitionTemplate
from ansys.rep.client.jms.schema.task_definition_template import TaskDefinitionTemplateSchema
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class TaskDefinitionTemplateTest(REPTestCase):
    def test_template_deserialization(self):

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
        }

        template = TaskDefinitionTemplateSchema().load(json_data)

        self.assertEqual(template.__class__.__name__, "TaskDefinitionTemplate")
        self.assertEqual(template.modification_time, missing)
        self.assertEqual(template.name, json_data["name"])
        self.assertEqual(template.execution_context["parallel_processing_type"].default, "DMP")
        self.assertEqual(len(template.execution_context["parallel_processing_type"].value_list), 3)
        self.assertTrue(
            "Hybrid" in template.execution_context["parallel_processing_type"].value_list
        )
        self.assertEqual(len(template.output_files), 2)
        self.assertEqual(template.output_files[0].name, "out")
        self.assertEqual(template.output_files[1].type, "application/octet-stream")

        json_data["software_requirements"][0]["version"] = "2022 R2"
        json_data["execution_command"] = "my command line"
        json_data["execution_context"] = {"my_new_field": {"default": "value", "type": "string"}}

        template = TaskDefinitionTemplateSchema().load(json_data)
        self.assertEqual(template.software_requirements[0].version, "2022 R2")
        self.assertEqual(template.execution_command, "my command line")
        self.assertEqual(template.execution_context["my_new_field"].default, "value")

    def test_template_integration(self):

        client = self.client()
        jms_api = JmsApi(client)

        # Test get queries
        templates = jms_api.get_task_definition_templates()
        self.assertGreater(len(templates), 0)
        self.assertTrue(templates[0].id is not None)

        templates = jms_api.get_task_definition_templates(as_objects=False)
        self.assertGreater(len(templates), 0)
        self.assertTrue(templates[0]["id"] is not None)

        templates = jms_api.get_task_definition_templates(
            as_objects=False, fields=["name", "software_requirements"]
        )
        self.assertGreater(len(templates), 0)
        log.info(f"templates={json.dumps(templates, indent=4)}")
        if templates:
            self.assertTrue("software_requirements" in templates[0].keys())
            self.assertTrue("name" in templates[0]["software_requirements"][0].keys())
            self.assertTrue("version" in templates[0]["software_requirements"][0].keys())

        templates = jms_api.get_task_definition_templates(fields=["name"])
        if templates:
            self.assertTrue(templates[0].software_requirements == missing)

        # Copy template
        template_name = f"copied_template_{uuid.uuid4()}"
        templates = jms_api.get_task_definition_templates(limit=1)
        self.assertEqual(len(templates), 1)

        template = TaskDefinitionTemplate(
            name=template_name, software_requirements=templates[0].software_requirements
        )
        template.version = "1.0"
        templates = jms_api.create_task_definition_templates([template])
        self.assertEqual(len(templates), 1)
        template = templates[0]
        self.assertEqual(template.name, template_name)

        # Modify copied template
        template.software_requirements[0].version = "2.0.1"
        templates = jms_api.update_task_definition_templates([template])
        self.assertEqual(len(templates), 1)
        template = templates[0]
        self.assertEqual(template.software_requirements[0].version, "2.0.1")
        self.assertEqual(template.name, template_name)

        # Delete copied template
        jms_api.delete_task_definition_templates([template])

        templates = jms_api.get_task_definition_templates(name=template_name)
        self.assertEqual(len(templates), 0)

    def test_template_permissions(self):

        client = self.client()
        jms_api = JmsApi(client)

        templates = jms_api.get_task_definition_templates()

        # a regular deployment should have some default templates
        # with read all permissions + some user defined ones with
        # either user or group permissions
        for template in templates:
            permissions = jms_api.get_task_definition_template_permissions(template_id=template.id)
            for permission in permissions:
                self.assertIn(permission.permission_type, ["user", "group", "anyone"])

        # create new template and check default permissions
        template = TaskDefinitionTemplate(name="my_template", version=uuid.uuid4())
        template = jms_api.create_task_definition_templates([template])[0]
        permissions = jms_api.get_task_definition_template_permissions(template_id=template.id)
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].permission_type, "user")
        self.assertEqual(permissions[0].role, "admin")
        self.assertIsNotNone(permissions[0].value_id)

        # create test user
        auth_api = AuthApi(client)
        user_credentials = {
            "user1": {"username": f"testuser-{uuid.uuid4().hex[:8]}", "password": "test"}
        }
        user1 = auth_api.create_user(
            User(
                username=user_credentials["user1"]["username"],
                password=user_credentials["user1"]["password"],
                is_admin=False,
            )
        )
        log.info(f"User 1: {user1}")
        client1 = Client(
            rep_url=self.rep_url,
            username=user1.username,
            password=user_credentials["user1"]["password"],
        )
        jms_api1 = JmsApi(client1)

        # verify test user can't access the template
        client1_templates = jms_api1.get_task_definition_templates(id=template.id)
        self.assertEqual(len(client1_templates), 0)

        # grant read all permissions
        permissions.append(Permission(permission_type="anyone", role="reader", value_id=None))
        permissions = jms_api.update_task_definition_template_permissions(template.id, permissions)
        self.assertEqual(len(permissions), 2)

        # verify test user can now access the template
        client1_templates = jms_api1.get_task_definition_templates(id=template.id)
        self.assertEqual(len(client1_templates), 1)
        self.assertEqual(client1_templates[0].name, template.name)

        # verify test user can't edit the template
        client1_templates[0].version = client1_templates[0].version + "-dev"

        except_obj = None
        try:
            client1_templates = jms_api1.update_task_definition_templates(client1_templates)
        except REPError as e:
            except_obj = e
        self.assertEqual(except_obj.response.status_code, 403)
        self.assertEqual(except_obj.description, "Access to this resource has been restricted")

        # grant write permissions to the user
        permissions.append(Permission(permission_type="user", role="writer", value_id=user1.id))
        permissions = jms_api.update_task_definition_template_permissions(template.id, permissions)
        self.assertEqual(len(permissions), 3)

        # verify test user can now edit the template
        client1_templates[0].version = client1_templates[0].version + "-dev"
        client1_templates = jms_api1.update_task_definition_templates(client1_templates)

        # Delete template
        jms_api.delete_task_definition_templates([template])

        # Let user1 create a template
        template = TaskDefinitionTemplate(name="my_template", version=uuid.uuid4())
        template = jms_api1.create_task_definition_templates([template])[0]
        template = jms_api1.get_task_definition_templates(id=template.id)[0]
        self.assertEqual(template.name, "my_template")
        permissions = jms_api1.get_task_definition_template_permissions(template_id=template.id)
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].permission_type, "user")
        self.assertEqual(permissions[0].role, "admin")
        self.assertEqual(permissions[0].value_id, user1.id)

        # verify that an admin user can access the template
        admin_templates = jms_api.get_task_definition_templates(id=template.id)
        log.info(admin_templates)
        self.assertEqual(len(admin_templates), 1)
        self.assertEqual(admin_templates[0].name, template.name)
        self.assertEqual(admin_templates[0].version, template.version)

        # Delete template
        jms_api1.delete_task_definition_templates([template])

        # Delete user
        auth_api.delete_user(user1)

    def test_template_anyone_permission(self):

        client = self.client()
        jms_api = JmsApi(client)

        # create new template and check default permissions
        template = TaskDefinitionTemplate(name="my_template", version=uuid.uuid4())
        template = jms_api.create_task_definition_templates([template])[0]
        permissions = jms_api.get_task_definition_template_permissions(template_id=template.id)
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].permission_type, "user")
        self.assertEqual(permissions[0].role, "admin")
        self.assertIsNotNone(permissions[0].value_id)

        # create test user
        auth_api = AuthApi(client)
        user_credentials = {
            "user1": {"username": f"testuser-{uuid.uuid4().hex[:8]}", "password": "test"}
        }
        user1 = auth_api.create_user(
            User(
                username=user_credentials["user1"]["username"],
                password=user_credentials["user1"]["password"],
                is_admin=False,
            )
        )
        log.info(f"User 1: {user1}")
        client1 = Client(
            rep_url=self.rep_url,
            username=user1.username,
            password=user_credentials["user1"]["password"],
        )
        jms_api1 = JmsApi(client1)

        # verify test user can't access the template
        client1_templates = jms_api1.get_task_definition_templates(id=template.id)
        self.assertEqual(len(client1_templates), 0)

        # grant read all permissions
        permissions.append(Permission(permission_type="anyone", role="reader", value_id=None))
        permissions = jms_api.update_task_definition_template_permissions(template.id, permissions)
        self.assertEqual(len(permissions), 2)

        # verify test user can now access the template
        client1_templates = jms_api1.get_task_definition_templates(id=template.id)
        self.assertEqual(len(client1_templates), 1)
        self.assertEqual(client1_templates[0].name, template.name)

        # verify test user can't edit the template
        client1_templates[0].version = client1_templates[0].version + "-dev"

        except_obj = None
        try:
            client1_templates = jms_api1.update_task_definition_templates(client1_templates)
        except REPError as e:
            except_obj = e
        self.assertEqual(except_obj.response.status_code, 403)
        self.assertEqual(except_obj.description, "Access to this resource has been restricted")

        # grant write all permissions
        anyone_permission = next(p for p in permissions if p.permission_type == "anyone")
        anyone_permission.role = "writer"
        permissions = jms_api.update_task_definition_template_permissions(template.id, permissions)
        self.assertEqual(len(permissions), 2)
        for p in permissions:
            if p.permission_type == "anyone":
                self.assertEqual(p.role, "writer")

        # verify test user can now edit the template
        client1_templates = jms_api1.update_task_definition_templates(client1_templates)

        # Delete template
        jms_api.delete_task_definition_templates([template])

        # Delete user
        auth_api.delete_user(user1)


if __name__ == "__main__":
    unittest.main()
