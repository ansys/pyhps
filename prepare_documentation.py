# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import os
import json
from zipfile import ZipFile

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from ansys.rep.client import __version__
from ansys.rep.client.jms.schema.object_reference import (IdReference, IdReferenceList)
from ansys.rep.client.jms.resource import (Project, ProjectPermission, LicenseContext,
    Job, Algorithm, Selection, JobDefinition, 
    ParameterMapping, FloatParameterDefinition, BoolParameterDefinition, IntParameterDefinition, StringParameterDefinition,
    Task, Evaluator,
    File, FitnessDefinition, FitnessTermDefinition,
    TaskDefinition, SuccessCriteria, Licensing, TaskDefinitionTemplate)

from ansys.rep.client.auth.resource import User

def custom_field_attributes(self, field, **kwargs):
    ret = {}
    if hasattr(field, "attribute"):
        if field.attribute is not None:
            ret["attribute"] = field.attribute
    if isinstance(field, IdReference):
        ret["custom_type"] = "string"
    elif isinstance(field, IdReferenceList):
        ret["custom_type"] = "array"

    return ret

def generate_openapi_specs():
    """Auto-generate schemas documentation in JSON format."""

    tgt_dir = os.path.join('doc', 'schemas')
    if not os.path.exists(tgt_dir):
        os.makedirs(tgt_dir)

    for resource in [Project, ProjectPermission, LicenseContext,
                      Job, Algorithm, Selection, JobDefinition, 
                      ParameterMapping, 
                      FloatParameterDefinition, BoolParameterDefinition, 
                      IntParameterDefinition, StringParameterDefinition,
                      Task, Evaluator, File, FitnessDefinition, FitnessTermDefinition,
                      TaskDefinition, SuccessCriteria, Licensing, TaskDefinitionTemplate,
                      User
                   ]:

        ma_plugin = MarshmallowPlugin() 
        spec = APISpec(
            title="pyrep",
            version=__version__,
            openapi_version="3.0",
            plugins=[ma_plugin],
        )

        ma_plugin.converter.add_attribute_function(custom_field_attributes)  
        object_name = resource.__name__
        spec.components.schema(object_name, schema=resource.Meta.schema)    
        prop_dict = spec.to_dict()['components']['schemas'][object_name]["properties"]

        modified_prop_dict = {}
        for k, v in prop_dict.items():
            if k == "obj_type":
                continue
            v.pop('additionalProperties', None)

            if "custom_type" in v:
                v["type"] = v["custom_type"]
            if "attribute" in v:
                new_key = v.pop("attribute")
                modified_prop_dict[new_key] = v
            else:
                modified_prop_dict[k] = v

        with open(f'{os.path.join(tgt_dir, object_name)}.json', 'w') as outfile:
           outfile.write( json.dumps( {"properties": modified_prop_dict}, indent=4) )

def archive_examples(examples):
    """Create a zip archive for each listed example included in the examples folder."""

    examples = {
        "mapdl_motorbike_frame" : ["project_setup.py", "motorbike_frame_results.txt", "motorbike_frame.mac"]
    }

    for name, files in examples.items():
        with ZipFile(f'{name}.zip', 'w') as zip_archive:
            for file in files:
                zip_archive.write(os.path.join('examples', name, file), file)

if __name__ == "__main__":
    generate_openapi_specs()
    archive_examples(['mapdl_motorbike_frame'])