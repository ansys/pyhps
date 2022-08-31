import os
import json
import importlib
import marshmallow
from ansys.rep.client.jms.schema.object_reference import IdReferenceList

resources = [
    { 
        "schema" : "JobDefinitionSchema",
        "schema_filename" : "job_definition",
        "rest_name": "job_definitions",
        "additional_fields": [],
        "class": "JobDefinition",
        "resource_filename" : "job_definition",
    },
    { 
        "schema" : "ResourceRequirementsSchema",
        "schema_filename" : "task_definition",
        "rest_name": None,
        "additional_fields": [],
        "class": "ResourceRequirements",
        "resource_filename" : "resource_requirements",
    },
    { 
        "schema" : "JobSchema",
        "schema_filename" : "job",
        "rest_name": "jobs",
        "additional_fields": [],
        "class": "Job",
        "resource_filename" : "job",
    },
    { 
        "schema" : "EvaluatorSchema",
        "schema_filename" : "evaluator",
        "rest_name": "evaluators",
        "additional_fields": [],
        "class": "Evaluator",
        "resource_filename" : "evaluator",
    }
]

FIELD_MAPPING = {
    marshmallow.fields.Integer: "int",
    marshmallow.fields.Float: "float",
    marshmallow.fields.String: "str", 
    marshmallow.fields.Boolean: "bool",
    marshmallow.fields.DateTime: "datetime",
    marshmallow.fields.Dict: "dict",
    marshmallow.fields.List: "list",
    IdReferenceList: "list"
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
        field_doc = f"{field}"
        type = FIELD_MAPPING.get(v.__class__, None)
        if type:
            field_doc += f" ({type})"
        desc = v.metadata.get("description", None)
        if desc:
            field_doc += f": {desc}"
        fields_doc.append(field_doc)
    return fields, fields_doc

def get_generated_code(resource, fields, field_docs):

    code =\
f'''
from marshmallow.utils import missing
from .base import Object
from ..schema.{resource['schema_filename']} import {resource['schema']}

class {resource['class']}(Object):
    """{resource['class']} resource.
    
    Parameters:
{field_docs}

    The {resource['class']} schema has the following fields:

    .. jsonschema:: schemas/{resource['class']}.json

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
    resource_class = getattr(module, resource['schema'])

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
    with open(file_path, 'w') as file:
        file.write(code)



#     imports=\
# f"""
# from marshmallow.utils import missing
# from .base import Object
# from ..schema.{resource['schema_filename']} import {resource['schema']}
# """

#     docstring = f'''"""{resource['class']} resource.
    
#     Args:
#         **kwargs: Arbitrary keyword arguments, see the {resource['class']} schema below.

#     The {resource['class']} schema has the following fields:

#     .. jsonschema:: schemas/{resource['class']}.json

#     """
# '''

#     class_definition=\
# f"""
# class {resource['class']}(Object):
#     {docstring}
#     class Meta:
#         schema = {resource['schema']}
#         rest_name = "{resource['rest_name']}"

#     def __init__(self, **kwargs):
# """

#     set_meta=\
# f"""
# {resource['schema']}.Meta.object_class = {resource['class']}
# """

#     module = importlib.import_module(f"ansys.rep.client.jms.schema.{resource['schema_filename']}")
#     resource_class = getattr(module, resource['schema'])
#     with open(os.path.join("ansys", "rep", "client", "jms", "resource", f"{resource['resource_filename']}.py"), 'w') as file:
#         file.write(imports)
#         file.write(class_definition)

#         for k in declared_fields(resource_class):
#             file.write(f"        self.{k} = missing\n")

#         file.write(f"        super().__init__(**kwargs)\n")

#         file.write(set_meta)