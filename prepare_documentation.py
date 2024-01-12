# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
import os
from zipfile import ZipFile

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from ansys.hps.client import __version__
from ansys.hps.client.auth.resource import User
from ansys.hps.client.jms.resource import (
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
    Permission,
    Project,
    ResourceRequirements,
    Software,
    StringParameterDefinition,
    SuccessCriteria,
    Task,
    TaskDefinition,
    TaskDefinitionTemplate,
)
from ansys.hps.client.jms.schema.object_reference import IdReference, IdReferenceList


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
        Permission,
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
            title="pyhps",
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

        with open(f"{os.path.join(tgt_dir, object_name)}.json", "w") as outfile:
            outfile.write(json.dumps({"properties": modified_prop_dict}, indent=4))


def archive_examples():
    """Create a zip archive for each listed example included in the examples folder."""

    examples = {
        "mapdl_motorbike_frame": [
            "project_setup.py",
            "project_query.py",
            "exec_mapdl.py",
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
            "exec_python.py",
            "evaluate.py",
            "input_parameters.json",
        ],
        "fluent_2d_heat_exchanger": [
            "project_setup.py",
            "heat_exchanger.jou",
            "heat_exchanger.cas.h5",
        ],
        "fluent_nozzle": [
            "project_setup.py",
            "exec_fluent.py",
            "solve.jou",
            "nozzle.cas",
        ],
        "cfx_static_mixer": [
            "project_setup.py",
            "exec_cfx.py",
            "runInput.ccl",
            "StaticMixer_001.cfx",
            "StaticMixer_001.def",
        ],
    }

    os.makedirs("build", exist_ok=True)
    for name, files in examples.items():
        with ZipFile(os.path.join("build", f"{name}.zip"), "w") as zip_archive:
            for file in files:
                zip_archive.write(os.path.join("examples", name, file), file)

    with ZipFile(os.path.join("build", f"pyhps_examples.zip"), "w") as zip_archive:
        for name, files in examples.items():
            for file in files:
                zip_archive.write(os.path.join("examples", name, file), os.path.join(name, file))


if __name__ == "__main__":
    # generate_openapi_specs()
    archive_examples()
