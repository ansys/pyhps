# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import json

from ..schema.task_definition_template import TaskDefinitionTemplateSchema
from .base import Object


class TaskDefinitionTemplate(Object):
    """TaskDefinitionTemplate resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the TaskDefinitionTemplate schema below.

    Example:

        >>> template = TaskDefinitionTemplate(
                    name="MAPDL_run",
                    application_name="ANSYS Mechanical APDL",
                    application_version="2022 R2",
                    data = {
                        "execution_command": "%executable% -b
                                              -i %file:mac% -o file.out
                                              -np %resource:num_cores%",
                        "output_files": [
                            {
                              "name": "out",
                              "obj_type": "File",
                              "evaluation_path": "solve.out",
                              "type": "text/plain",
                              "collect": true,
                              "monitor": true
                            }
                        ]
                    }
                )

    The TaskDefinitionTemplate schema has the following fields:

    .. jsonschema:: schemas/TaskDefinitionTemplate.json

    """

    class Meta:
        schema = TaskDefinitionTemplateSchema

    def __init__(self, **kwargs):
        super(TaskDefinitionTemplate, self).__init__(**kwargs)


TaskDefinitionTemplateSchema.Meta.object_class = TaskDefinitionTemplate


def get_task_definition_templates(client, as_objects=True, **query_params):
    """
    Returns list of task definition templates
    """

    url = f"{client.jms_api_url}/task_definition_templates"
    r = client.session.get(url, params=query_params)

    data = r.json()["task_definition_templates"]
    if not as_objects:
        return data

    templates = TaskDefinitionTemplateSchema(many=True).load(data)
    return templates


def update_task_definition_templates(client, templates):
    """
    Update task definition templates
    """
    url = f"{client.jms_api_url}/task_definition_templates"

    schema = TaskDefinitionTemplateSchema(many=True)
    serialized_data = schema.dump(templates)
    json_data = json.dumps({"task_definition_templates": serialized_data})

    r = client.session.put(f"{url}", data=json_data)

    data = r.json()["task_definition_templates"]

    objects = schema.load(data)
    return objects


def create_task_definition_templates(client, templates):
    """
    Create task definition templates
    """
    url = f"{client.jms_api_url}/task_definition_templates"

    schema = TaskDefinitionTemplateSchema(many=True)
    serialized_data = schema.dump(templates)
    json_data = json.dumps({"task_definition_templates": serialized_data})

    print(json.dumps({"task_definition_templates": serialized_data}, indent=4))

    r = client.session.post(f"{url}", data=json_data)

    data = r.json()["task_definition_templates"]

    objects = schema.load(data)
    return objects


def delete_task_definition_templates(client, templates):
    """
    Delete task definition templates
    """
    url = f"{client.jms_api_url}/task_definition_templates"

    json_data = json.dumps({"source_ids": [obj.id for obj in templates]})
    r = client.session.delete(f"{url}", data=json_data)
