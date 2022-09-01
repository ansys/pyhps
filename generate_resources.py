"""
Script to auto generate (most of the) JMS Resources.
Main aim is to auto-generate the class docstrings and
allows code completion (intellisense).
"""

import importlib
import os

import marshmallow

from ansys.rep.client.jms.schema.object_reference import IdReference, IdReferenceList

# we define here which resources to auto-generate
# some are excluded or done only partially (e.g. File)
# because they require more customization
JMS_RESOURCES = [
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
        "schema": "FitnessDefinitionSchema",
        "schema_filename": "fitness_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "FitnessDefinitionBase",
        "resource_filename": "fitness_definition_base",
    },
    {
        "schema": "FitnessTermDefinitionSchema",
        "schema_filename": "fitness_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "FitnessTermDefinitionBase",
        "resource_filename": "fitness_term_definition_base",
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
        "schema": "SoftwareSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "Software",
        "resource_filename": "software",
    },
    {
        "schema": "SuccessCriteriaSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "SuccessCriteria",
        "resource_filename": "success_criteria",
    },
    {
        "schema": "LicensingSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "Licensing",
        "resource_filename": "licensing",
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
        "schema": "TaskDefinitionSchema",
        "schema_filename": "task_definition",
        "rest_name": "task_definitions",
        "additional_fields": [],
        "class": "TaskDefinition",
        "resource_filename": "task_definition",
    },
    {
        "schema": "TaskSchema",
        "schema_filename": "task",
        "rest_name": "tasks",
        "additional_fields": [],
        "class": "Task",
        "resource_filename": "task",
    },
    {
        "schema": "ParameterDefinitionSchema",
        "schema_filename": "parameter_definition",
        "rest_name": "parameter_definitions",
        "additional_fields": [],
        "class": "ParameterDefinition",
        "resource_filename": "parameter_definition",
    },
    {
        "schema": "FloatParameterDefinitionSchema",
        "schema_filename": "parameter_definition",
        "rest_name": "parameter_definitions",
        "additional_fields": [],
        "base_class": "ParameterDefinition",
        "class": "FloatParameterDefinition",
        "resource_filename": "float_parameter_definition",
    },
    {
        "schema": "IntParameterDefinitionSchema",
        "schema_filename": "parameter_definition",
        "rest_name": "parameter_definitions",
        "additional_fields": [],
        "base_class": "ParameterDefinition",
        "class": "IntParameterDefinition",
        "resource_filename": "int_parameter_definition",
    },
    {
        "schema": "BoolParameterDefinitionSchema",
        "schema_filename": "parameter_definition",
        "rest_name": "parameter_definitions",
        "additional_fields": [],
        "base_class": "ParameterDefinition",
        "class": "BoolParameterDefinition",
        "resource_filename": "bool_parameter_definition",
    },
    {
        "schema": "StringParameterDefinitionSchema",
        "schema_filename": "parameter_definition",
        "rest_name": "parameter_definitions",
        "additional_fields": [],
        "base_class": "ParameterDefinition",
        "class": "StringParameterDefinition",
        "resource_filename": "string_parameter_definition",
    },
]

AUTH_RESOURCES = [
    {
        "schema": "UserSchema",
        "schema_filename": "user",
        "rest_name": None,
        "additional_fields": [],
        "base_class": "Object",
        "class": "User",
        "resource_filename": "user",
    },
]

# mapping of marshmallow field types to doc types
FIELD_MAPPING = {
    marshmallow.fields.Integer: "int",
    marshmallow.fields.Float: "float",
    marshmallow.fields.String: "str",
    marshmallow.fields.Boolean: "bool",
    marshmallow.fields.DateTime: "datetime",
    marshmallow.fields.Dict: "dict",
    marshmallow.fields.List: "list",
    IdReferenceList: "list[str]",
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


def get_generated_code(resource, base_class, fields, field_docs):

    base_class_import = (
        f"from {base_class['path']}.{base_class['filename']} import {base_class['name']}"
    )

    code = f'''# autogenerated code based on {resource["schema"]}

from marshmallow.utils import missing
{base_class_import}
from ..schema.{resource['schema_filename']} import {resource['schema']}

class {resource['class']}({base_class["name"]}):
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


def process_resources(subpackage, resources, base_class_path=""):

    targe_folder = os.path.join("ansys", "rep", "client", subpackage, "resource")
    for resource in resources:
        print(f"Processing resource {resource['class']}")

        # dynamically load resource schema
        module = importlib.import_module(
            f"ansys.rep.client.{subpackage}.schema.{resource['schema_filename']}"
        )
        resource_class = getattr(module, resource["schema"])

        # query schema field names and doc
        fields, field_docs = declared_fields(resource_class)

        fields_str = ""
        for k in fields:
            fields_str += f"        self.{k} = missing\n"

        field_docs_str = ""
        for k in field_docs:
            field_docs_str += f"        {k}\n"

        print(f"Class init parameters:\n{field_docs_str}")

        # if a base class other than Object need to be used,
        # we need to make sure to properly import it in the generated code
        base_class = {"name": "Object", "filename": "base", "path": base_class_path}
        if resource.get("base_class", None):
            base_class["name"] = resource["base_class"]
            base_class["filename"] = next(
                (r["resource_filename"] for r in resources if r["class"] == resource["base_class"]),
                None,
            )

        # we're ready to put the pieces together
        code = get_generated_code(resource, base_class, fields_str, field_docs_str)

        # dump generated code to file
        file_path = os.path.join(targe_folder, f"{resource['resource_filename']}.py")
        with open(file_path, "w") as file:
            file.write(code)


def run():
    process_resources("jms", JMS_RESOURCES)
    process_resources("auth", AUTH_RESOURCES, base_class_path="ansys.rep.client.jms.resource")


if __name__ == "__main__":
    run()
