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

"""Script to auto generate (most of the) JMS Resources.

The main goal is to auto-generate the class docstrings and
allow code completion.
"""

import importlib
import os
from dataclasses import dataclass

import marshmallow

from ansys.hps.client.common.restricted_value import RestrictedValue
from ansys.hps.client.jms.schema.object_reference import IdReference, IdReferenceList

# we define here which resources to auto-generate
# some are excluded or done only partially (File and FitnessDefinition)
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
        "schema": "FileSchema",
        "schema_filename": "file",
        "rest_name": "files",
        "additional_fields": [],
        "class": "File",
        "resource_filename": "file_base",
    },
    {
        "schema": "FitnessDefinitionSchema",
        "schema_filename": "fitness_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "FitnessDefinition",
        "resource_filename": "fitness_definition_base",
        "additional_imports": [
            "from .fitness_term_definition_base import FitnessTermDefinition",
        ],
    },
    {
        "schema": "FitnessTermDefinitionSchema",
        "schema_filename": "fitness_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "FitnessTermDefinition",
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
        "additional_imports": [
            "from .fitness_definition import FitnessDefinition",
        ],
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
        "schema": "PermissionSchema",
        "schema_filename": "permission",
        "rest_name": "permissions",
        "additional_fields": [],
        "class": "Permission",
        "resource_filename": "permission",
    },
    {
        "schema": "HpcResourcesSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "HpcResources",
        "resource_filename": "task_definition",
    },
    {
        "schema": "ResourceRequirementsSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "ResourceRequirements",
        "resource_filename": "task_definition",
    },
    {
        "schema": "SoftwareSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "Software",
        "resource_filename": "task_definition",
    },
    {
        "schema": "WorkerContextSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "WorkerContext",
        "resource_filename": "task_definition",
    },
    {
        "schema": "SuccessCriteriaSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "SuccessCriteria",
        "resource_filename": "task_definition",
    },
    {
        "schema": "LicensingSchema",
        "schema_filename": "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "Licensing",
        "resource_filename": "task_definition",
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
        "schema": "JobSelectionSchema",
        "schema_filename": "selection",
        "rest_name": "job_selections",
        "additional_fields": [],
        "class": "JobSelection",
        "resource_filename": "selection",
    },
    {
        "schema": "TemplateSoftwareSchema",
        "schema_filename": "task_definition_template",
        "rest_name": None,
        "additional_fields": [],
        "class": "TemplateSoftware",
        "resource_filename": "task_definition_template",
    },
    {
        "schema": "TemplatePropertySchema",
        "schema_filename": "task_definition_template",
        "rest_name": None,
        "additional_fields": [],
        "class": "TemplateProperty",
        "resource_filename": "task_definition_template",
    },
    {
        "schema": "TemplateResourceRequirementsSchema",
        "schema_filename": "task_definition_template",
        "rest_name": None,
        "additional_fields": [],
        "class": "TemplateResourceRequirements",
        "resource_filename": "task_definition_template",
    },
    {
        "schema": "TemplateInputFileSchema",
        "schema_filename": "task_definition_template",
        "rest_name": None,
        "additional_fields": [],
        "class": "TemplateInputFile",
        "resource_filename": "task_definition_template",
    },
    {
        "schema": "TemplateOutputFileSchema",
        "schema_filename": "task_definition_template",
        "rest_name": None,
        "additional_fields": [],
        "class": "TemplateOutputFile",
        "resource_filename": "task_definition_template",
    },
    {
        "schema": "TaskDefinitionTemplateSchema",
        "schema_filename": "task_definition_template",
        "rest_name": "task_definition_templates",
        "additional_fields": [],
        "class": "TaskDefinitionTemplate",
        "resource_filename": "task_definition_template",
        "additional_imports": [
            "from .task_definition import HpcResources, Software, WorkerContext"
        ],
    },
    {
        "schema": "TaskSchema",
        "schema_filename": "task",
        "rest_name": "tasks",
        "additional_fields": [],
        "class": "Task",
        "resource_filename": "task",
        "additional_imports": ["from .task_definition import TaskDefinition"],
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
        "resource_filename": "parameter_definition",
    },
    {
        "schema": "IntParameterDefinitionSchema",
        "schema_filename": "parameter_definition",
        "rest_name": "parameter_definitions",
        "additional_fields": [],
        "base_class": "ParameterDefinition",
        "class": "IntParameterDefinition",
        "resource_filename": "parameter_definition",
    },
    {
        "schema": "BoolParameterDefinitionSchema",
        "schema_filename": "parameter_definition",
        "rest_name": "parameter_definitions",
        "additional_fields": [],
        "base_class": "ParameterDefinition",
        "class": "BoolParameterDefinition",
        "resource_filename": "parameter_definition",
    },
    {
        "schema": "StringParameterDefinitionSchema",
        "schema_filename": "parameter_definition",
        "rest_name": "parameter_definitions",
        "additional_fields": [],
        "base_class": "ParameterDefinition",
        "class": "StringParameterDefinition",
        "resource_filename": "parameter_definition",
    },
    {
        "schema": "TaskCommandDefinitionSchema",
        "schema_filename": "task_command_definition",
        "rest_name": "task_command_definitions",
        "additional_fields": [],
        "class": "TaskCommandDefinition",
        "resource_filename": "task_command_definition",
    },
    {
        "schema": "TaskCommandSchema",
        "schema_filename": "task_command",
        "rest_name": "task_commands",
        "additional_fields": [],
        "class": "TaskCommand",
        "resource_filename": "task_command",
    },
]

AUTH_RESOURCES = [
    {
        "schema": "UserSchema",
        "schema_filename": "user",
        "rest_name": None,
        "additional_fields": [],
        "class": "User",
        "resource_filename": "user",
    },
]

# mapping of marshmallow field types to types

FIELD_MAPPING = {
    marshmallow.fields.Integer: "int",
    marshmallow.fields.Float: "float",
    marshmallow.fields.String: "str",
    marshmallow.fields.Boolean: "bool",
    marshmallow.fields.DateTime: "datetime",
    marshmallow.fields.Dict: "dict",
    marshmallow.fields.List: "list",
    marshmallow.fields.Constant: "Constant",
    marshmallow.fields.Nested: "object",
    IdReferenceList: "list[str]",
    IdReference: "str",
    RestrictedValue: "Union[int, float, str, bool]",
}

FILE_HEADER = """# DO NOT EDIT.
# This file is automatically generated from the JMS schemas.

"""


@dataclass
class Field:
    name: str
    type: str = "Any"


def extract_field_info(name: str, field_object: marshmallow.fields, resources) -> tuple[Field, str]:
    field = Field(name=name)
    v = field_object

    # Ensure that we use the attribute name if defined
    if getattr(v, "attribute", None) is not None:
        field.name = v.attribute

    # build attribute doc
    field_doc = f"{field.name}"

    field_type = _extract_field_type(v, resources)
    if field_type:
        field_doc += f" : {field_type}"
        if v.allow_none:
            field_doc += ", optional"
        field_doc += "\n"
        field.type = field_type.replace("list", "List").replace("dict", "Dict")
    elif v.allow_none:
        field_doc += " : any, optional\n"
    desc = v.metadata.get("description", None)
    if desc:
        field_doc += f"        {desc}\n"

    return field, field_doc


def _extract_field_type(v, resources) -> str:
    if v.__class__ == marshmallow.fields.Constant:
        field_type = type(v.constant).__name__
    elif v.__class__ == marshmallow.fields.Nested:
        field_type_schema = v.nested.__name__
        field_type = next(
            (r["class"] for r in resources if r["schema"] == field_type_schema),
            "object",
        )
    else:
        field_type = FIELD_MAPPING.get(v.__class__, None)
    if field_type:
        if v.__class__ == marshmallow.fields.Dict:
            if v.key_field:
                key_field_type = _extract_field_type(v.key_field, resources)
                if v.value_field:
                    value_field_type = _extract_field_type(v.value_field, resources)
                else:
                    value_field_type = "any"
                field_type += f"[{key_field_type}, {value_field_type}]"
        if hasattr(v, "many") and v.many:
            field_type = f"list[{field_type}]"

    return field_type


def declared_fields(schema, resources) -> tuple[list[Field], list[str]]:
    """Helper function to retrieve the fields that is defined as class members for an object"""
    fields = []
    fields_doc = []
    for k, v in schema._declared_fields.items():
        field, field_doc = extract_field_info(k, v, resources)
        fields.append(field)
        fields_doc.append(field_doc)

    return fields, fields_doc


def get_resource_imports(resource, base_class):
    imports = [
        "from datetime import datetime",
        "from typing import List, Dict, Any, Union",
        "from marshmallow.utils import missing",
        "from ansys.hps.client.common import Object",
        # f"from {base_class['path']}.{base_class['filename']} import {base_class['name']}",
        f"from ..schema.{resource['schema_filename']} import {resource['schema']}",
    ]
    if "additional_imports" in resource:
        imports.extend(resource["additional_imports"])
    return imports


def camel_case_split(text: str) -> str:
    words = [[text[0]]]

    for c in text[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    words = ["".join(word) for word in words]
    return " ".join([w.lower() for w in words])


def get_module_docstring(file_name: str) -> str:
    module_name = " ".join(file_name.split("_"))
    code = f'''"""Module providing the {module_name} resource."""
'''
    return code


def get_resource_code(resource, base_class, fields: list[Field], field_docs: list[str]):
    fields_str = ""
    for k in fields:
        fields_str += f"        self.{k.name} = {k.name}\n"
    init_fields_str = ",\n".join([f"        {k.name}: {k.type} = missing" for k in fields])

    additional_initialization = "        self.obj_type = self.__class__.__name__"
    if resource.get("init_with_kwargs", True):
        if init_fields_str:
            init_fields_str += ",\n        **kwargs"
        else:
            init_fields_str = "        **kwargs"

    code = f'''class {resource["class"]}({base_class["name"]}):
    """Provides the {camel_case_split(resource["class"])} resource.

    Parameters
    ----------
{field_docs.rstrip()}
    """

    class Meta:
        schema = {resource["schema"]}
        rest_name = "{resource["rest_name"]}"

    def __init__(
        self,
{init_fields_str}
    ):
{fields_str}
{additional_initialization}


{resource["schema"]}.Meta.object_class = {resource["class"]}
'''
    return code


def process_resources(subpackage, resources, base_class_path="ansys.hps.client"):
    target_folder = os.path.join("src", "ansys", "hps", "client", subpackage, "resource")
    resources_code = {}
    for resource in resources:
        print(f"Processing resource {resource['class']}")

        # dynamically load resource schema
        module = importlib.import_module(
            f"ansys.hps.client.{subpackage}.schema.{resource['schema_filename']}"
        )
        resource_class = getattr(module, resource["schema"])

        # query schema field names and doc
        fields, field_docs = declared_fields(resource_class, resources)

        field_docs_str = ""
        for k in field_docs:
            field_docs_str += f"    {k}"

        print(f"Class init parameters:\n{field_docs_str}")

        # if a base class other than Object need to be used,
        # we need to make sure to properly import it in the generated code
        base_class = {"name": "Object", "filename": "common", "path": base_class_path}
        if resource.get("base_class", None):
            base_class["name"] = resource["base_class"]
            base_class["path"] = "ansys.hps.client.jms.resource"
            base_class["filename"] = next(
                (r["resource_filename"] for r in resources if r["class"] == resource["base_class"]),
                None,
            )

        # we're ready to put the pieces together
        file_name = resource["resource_filename"]
        if file_name not in resources_code:
            resources_code[file_name] = {
                "imports": [],
                "code": [],
                "module_docstring": get_module_docstring(file_name),
            }

        resources_code[file_name]["imports"].extend(get_resource_imports(resource, base_class))
        resources_code[file_name]["code"].append(
            get_resource_code(resource, base_class, fields, field_docs_str)
        )

    # dump generated code to files
    for file_n, content in resources_code.items():
        file_path = os.path.join(target_folder, f"{file_n}.py")
        print(f"=== file={file_n}, file_path={file_path}")
        unique_imports = list(dict.fromkeys(content["imports"]))
        code = content["code"]
        with open(file_path, "w") as file:
            file.write(FILE_HEADER)
            file.write(content["module_docstring"])
            file.write("\n".join(unique_imports))
            file.write("\n\n")
            file.write("\n".join(code))


def run():
    process_resources("jms", JMS_RESOURCES)
    process_resources("auth", AUTH_RESOURCES)


if __name__ == "__main__":
    run()
