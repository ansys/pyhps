# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

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
        rest_name = "task_definition_templates"

    def __init__(self, **kwargs):
        super(TaskDefinitionTemplate, self).__init__(**kwargs)


TaskDefinitionTemplateSchema.Meta.object_class = TaskDefinitionTemplate
