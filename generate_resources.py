import importlib
import os

import marshmallow

from ansys.rep.client.jms.schema.object_reference import IdReference, IdReferenceList

resources = [
    {
        "schema": "AlgorithmSchema",
        "schema_filename": "algorithm",
        "rest_name": "algorithms",
        "additional_fields": [],
        "class": "Algorithm",
        "resource_filename": "algorithm",
    },
    {
        "schema": "EvaluatorSchema",
        "schema_filename": "evaluator",
        "rest_name": "evaluators",
        "additional_fields": [],
        "class": "Evaluator",
        "resource_filename": "evaluator",
    },
    {
        "schema": "FileSchema",
        "schema_filename": "file",
        "rest_name": "files",
        "additional_fields": [],
        "class": "FileBase",
        "resource_filename": "file_base",
    },
    {
        "schema": "JobSchema",
        "schema_filename": "job",
        "rest_name": "jobs",
        "additional_fields": [],
        "class": "Job",
        "resource_filename": "job",
    },
    {
        "schema": "JobDefinitionSchema",
        "schema_filename": "job_definition",
        "rest_name": "job_definitions",
        "additional_fields": [],
        "class": "JobDefinition",
        "resource_filename": "job_definition",
    },
    {
        "schema": "LicenseContextSchema",
        "schema_filename": "license_context",
        "rest_name": "license_contexts",
        "additional_fields": [],
        "class": "LicenseContext",
        "resource_filename": "license_context",
    },
    {
        "schema": "OperationSchema",
        "schema_filename": "operation",
        "rest_name": "operations",
        "additional_fields": [],
        "class": "Operation",
        "resource_filename": "operation",
    },
    {
        "schema": "ParameterMappingSchema",
        "schema_filename": "parameter_mapping",
        "rest_name": "parameter_mappings",
        "additional_fields": [],
        "class": "ParameterMapping",
        "resource_filename": "parameter_mapping",
    },
    {
        "schema": "ProjectSchema",
        "schema_filename": "project",
        "rest_name": "projects",
        "additional_fields": [],
        "class": "Project",
        "resource_filename": "project",
    },
    {
        "schema": "ProjectPermissionSchema",
        "schema_filename": "project_permission",
        "rest_name": "permissions",
        "additional_fields": [],
        "class": "ProjectPermission",
        "resource_filename": "project_permission",
    },
    {
        "schema": "ResourceRequirementsSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "ResourceRequirements",
        "resource_filename": "resource_requirements",
    },
    {
        "schema": "JobSelectionSchema",
        "schema_filename": "selection",
        "rest_name": "job_selections",
        "additional_fields": [],
        "class": "JobSelection",
        "resource_filename": "selection",
    },
    {
        "schema": "TaskDefinitionTemplateSchema",
        "schema_filename": "task_definition_template",
        "rest_name": "task_definition_templates",
        "additional_fields": [],
        "class": "TaskDefinitionTemplate",
        "resource_filename": "task_definition_template",
    },
    {
        "schema": "TaskSchema",
        "schema_filename": "task",
        "rest_name": "tasks",
        "additional_fields": [],
        "class": "Task",
        "resource_filename": "task",
    },
]

FIELD_MAPPING = {
    marshmallow.fields.Integer: "int",
    marshmallow.fields.Float: "float",
    marshmallow.fields.String: "str",
    marshmallow.fields.Boolean: "bool",
    marshmallow.fields.DateTime: "datetime",
    marshmallow.fields.Dict: "dict",
    marshmallow.fields.List: "list",
    IdReferenceList: "list",
    IdReference: "str",
}


def declared_fields(schema):
    """
    Helper function to retrieve the fields that will be defined as class members for an object
    """
    fields = []
    fields_doc = []
    for k, v in schema._declared_fields.items():
        field = k
        # Ensure that we use the attribute name if defined
        if getattr(v, "attribute", None) is not None:
            field = v.attribute
        fields.append(field)

        # build attribute doc
        field_doc = f"{field}"
        type = FIELD_MAPPING.get(v.__class__, None)
        if type:
            field_doc += f" ({type}"
            if v.allow_none:
                field_doc += ", optional"
            field_doc += ")"
        elif v.allow_none:
            field_doc += " (optional)"
        desc = v.metadata.get("description", None)
        if desc:
            field_doc += f": {desc}"
        fields_doc.append(field_doc)
    return fields, fields_doc


def get_generated_code(resource, fields, field_docs):

    code = f'''
from marshmallow.utils import missing
from .base import Object
from ..schema.{resource['schema_filename']} import {resource['schema']}

class {resource['class']}(Object):
    """{resource['class']} resource.

    Parameters:
{field_docs}
    """

    class Meta:
        schema = {resource['schema']}
        rest_name = "{resource['rest_name']}"

    def __init__(self, **kwargs):
{fields}
        super().__init__(**kwargs)

{resource['schema']}.Meta.object_class = {resource['class']}
'''
    return code


targe_folder = os.path.join("ansys", "rep", "client", "jms", "resource")

for resource in resources:

    print(f"Processing resource {resource['class']}")

    module = importlib.import_module(f"ansys.rep.client.jms.schema.{resource['schema_filename']}")
    resource_class = getattr(module, resource["schema"])

    fields, field_docs = declared_fields(resource_class)

    fields_str = ""
    for k in fields:
        fields_str += f"        self.{k} = missing\n"

    field_docs_str = ""
    for k in field_docs:
        field_docs_str += f"        {k}\n"

    print(f"Attributes:\n{field_docs_str}")

    code = get_generated_code(resource, fields_str, field_docs_str)

    file_path = os.path.join(targe_folder, f"{resource['resource_filename']}.py")
    with open(file_path, "w") as file:
        file.write(code)
