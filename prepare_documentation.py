# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import json
import os
from zipfile import ZipFile

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from ansys.rep.client import __version__
from ansys.rep.client.auth.resource import User
from ansys.rep.client.jms.resource import (
    Algorithm,
    BoolParameterDefinition,
    Evaluator,
    File,
    FitnessDefinition,
    FitnessTermDefinition,
    FloatParameterDefinition,
    IntParameterDefinition,
    Job,
    JobDefinition,
    JobSelection,
    LicenseContext,
    Licensing,
    Operation,
    ParameterMapping,
    Project,
    ProjectPermission,
    ResourceRequirements,
    Software,
    StringParameterDefinition,
    SuccessCriteria,
    Task,
    TaskDefinition,
    TaskDefinitionTemplate,
)
from ansys.rep.client.jms.schema.object_reference import IdReference, IdReferenceList


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

    tgt_dir = os.path.join("doc", "source", "api", "schemas")
    if not os.path.exists(tgt_dir):
        os.makedirs(tgt_dir)

    for resource in [
        Project,
        ProjectPermission,
        LicenseContext,
        Job,
        Algorithm,
        JobSelection,
        JobDefinition,
        ParameterMapping,
        FloatParameterDefinition,
        BoolParameterDefinition,
        IntParameterDefinition,
        StringParameterDefinition,
        Task,
        Evaluator,
        File,
        FitnessDefinition,
        FitnessTermDefinition,
        TaskDefinition,
        SuccessCriteria,
        Software,
        ResourceRequirements,
        Licensing,
        TaskDefinitionTemplate,
        User,
        Operation,
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
        prop_dict = spec.to_dict()["components"]["schemas"][object_name]["properties"]

        modified_prop_dict = {}
        for k, v in prop_dict.items():
            if k == "obj_type":
                continue
            v.pop("additionalProperties", None)

            if "custom_type" in v:
                v["type"] = v["custom_type"]
            if "attribute" in v:
                new_key = v.pop("attribute")
                modified_prop_dict[new_key] = v
            else:
                modified_prop_dict[k] = v

            # User.is_admin is Function field which doesn't get the type
            if k == "is_admin":
                v["type"] = "boolean"

        with open(f"{os.path.join(tgt_dir, object_name)}.json", "w") as outfile:
            outfile.write(json.dumps({"properties": modified_prop_dict}, indent=4))


def archive_examples(examples):
    """Create a zip archive for each listed example included in the examples folder."""

    examples = {
        "mapdl_motorbike_frame": [
            "project_setup.py",
            "project_query.py",
            "motorbike_frame_results.txt",
            "motorbike_frame.mac",
        ],
        "mapdl_tyre_performance": [
            "project_setup.py",
            "tire_performance_simulation.mac",
            "2d_tire_geometry.iges",
        ],
        "mapdl_linked_analyses": [
            "project_setup.py",
            "prestress.dat",
            "modal.dat",
            "harmonic.dat",
        ],
        "lsdyna_cylinder_plate": [
            "lsdyna_job.py",
            "cylinder_plate.k",
            "postprocess.cfile",
        ],
        "python_two_bar_truss_problem": [
            "project_setup.py",
            "evaluate.py",
            "input_parameters.json",
        ],
    }

    os.makedirs("build", exist_ok=True)
    for name, files in examples.items():
        with ZipFile(os.path.join("build", f"{name}.zip"), "w") as zip_archive:
            for file in files:
                zip_archive.write(os.path.join("examples", name, file), file)

    with ZipFile(os.path.join("build", f"pyrep_examples.zip"), "w") as zip_archive:
        for name, files in examples.items():
            for file in files:
                zip_archive.write(os.path.join("examples", name, file), os.path.join(name, file))


if __name__ == "__main__":
    generate_openapi_specs()
    archive_examples(
        [
            "mapdl_motorbike_frame",
            "mapdl_tyre_performance",
            "mapdl_linked_analyses",
            "lsdyna_cylinder_plate",
        ]
    )
