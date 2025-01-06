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

import logging

from marshmallow.utils import missing

from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import (
    BoolParameterDefinition,
    FloatParameterDefinition,
    IntParameterDefinition,
    JobDefinition,
    Project,
    StringParameterDefinition,
)
from ansys.hps.client.jms.schema.parameter_definition import (
    BoolParameterDefinitionSchema,
    FloatParameterDefinitionSchema,
    IntParameterDefinitionSchema,
    ParameterDefinitionSchema,
    StringParameterDefinitionSchema,
)

log = logging.getLogger(__name__)


def test_parameter_definition_deserialization():

    int_parameter = {
        "default": 4,
        "lower_limit": 0,
        "upper_limit": 40,
        "step": 1,
        "cyclic": False,
        "quantity_name": "number",
        "units": None,
        "display_text": None,
        "mode": "input",
        "name": "num_layers",
        "id": "02q3Tt7pRqT3h0fNkOVMH1",
        "type": "int",
    }

    ip = IntParameterDefinitionSchema().load(int_parameter)
    assert ip.__class__.__name__ == "IntParameterDefinition"
    assert ip.type == "int"
    assert ip.id == int_parameter["id"]
    assert ip.name == int_parameter["name"]
    assert ip.mode == "input"
    assert ip.cyclic == False
    assert ip.upper_limit == 40
    assert ip.quantity_name == int_parameter["quantity_name"]

    float_parameter = {
        "default": 1.0,
        "lower_limit": 0.5,
        "step": None,
        "cyclic": False,
        "quantity_name": None,
        "units": "kg",
        "display_text": "say my name",
        "mode": "output",
        "name": "FBL_S2_ScalingY",
        "value_list": None,
        "id": "02q3Tt7pUIjPf8WekSCyeW",
        "type": "float",
    }

    fp = FloatParameterDefinitionSchema().load(float_parameter)
    assert fp.__class__.__name__ == "FloatParameterDefinition"
    assert fp.type == "float"
    assert fp.id == float_parameter["id"]
    assert fp.name == float_parameter["name"]
    assert fp.mode == "output"
    assert fp.step == None
    assert fp.lower_limit == 0.5
    assert fp.upper_limit == missing
    assert fp.display_text == float_parameter["display_text"]
    assert fp.units == float_parameter["units"]

    string_parameter = {
        "default": "1",
        "quantity_name": None,
        "display_text": None,
        "mode": "input",
        "name": "tube4",
        "value_list": ["steel", "carbon", "resin"],
        "id": "02q3Tt7pUwBe1GcX3WMYvs",
        "type": "string",
    }

    sp = StringParameterDefinitionSchema().load(string_parameter)
    assert sp.__class__.__name__ == "StringParameterDefinition"
    assert sp.type == "string"
    assert sp.id == string_parameter["id"]
    assert sp.name == string_parameter["name"]
    assert sp.quantity_name == None
    assert sp.value_list == ["steel", "carbon", "resin"]

    bool_parameter = {
        "default": True,
        "quantity_name": None,
        "units": None,
        "display_text": None,
        "mode": "input",
        "name": "tube4",
        "id": "02q3Tt7pchrYQ1PBlsgFbW",
        "type": "bool",
    }

    bp = BoolParameterDefinitionSchema().load(bool_parameter)
    assert bp.__class__.__name__ == "BoolParameterDefinition"
    assert bp.type == "bool"
    assert bp.id == bool_parameter["id"]
    assert bp.name == bool_parameter["name"]
    assert bp.default == True

    parameter_definitions = ParameterDefinitionSchema().load(
        [int_parameter, float_parameter, string_parameter, bool_parameter], many=True
    )
    assert parameter_definitions[0].__class__.__name__ == "IntParameterDefinition"
    assert parameter_definitions[1].__class__.__name__ == "FloatParameterDefinition"
    assert parameter_definitions[2].__class__.__name__ == "StringParameterDefinition"
    assert parameter_definitions[3].__class__.__name__ == "BoolParameterDefinition"


def test_parameter_definition_serialization():

    ip = IntParameterDefinition(name="int_param", upper_limit=27, mode="input")

    assert ip.quantity_name == missing
    assert ip.display_text == missing
    assert ip.lower_limit == missing
    assert ip.mode == "input"

    serialized_ip = IntParameterDefinitionSchema().dump(ip)

    assert not "display_text" in serialized_ip.keys()
    assert not "lower_limit" in serialized_ip.keys()
    assert serialized_ip["type"] == "int"
    assert serialized_ip["name"] == "int_param"
    assert serialized_ip["upper_limit"] == 27
    assert not "mode" in serialized_ip.keys()

    sp = StringParameterDefinition(name="s_param", value_list=["l1", "l2"])
    serialized_sp = StringParameterDefinitionSchema().dump(sp)
    assert serialized_sp["type"] == "string"
    assert serialized_sp["value_list"] == ["l1", "l2"]

    serialized_param_defs = ParameterDefinitionSchema().dump([ip, sp], many=True)

    assert len(serialized_param_defs) == 2
    assert not "id" in serialized_param_defs[0].keys()
    assert serialized_param_defs[0]["type"] == "int"
    assert serialized_param_defs[1]["type"] == "string"
    assert not "display_text" in serialized_param_defs[0].keys()
    assert serialized_param_defs[1]["name"] == "s_param"


def test_parameter_definition_integration(client):

    proj_name = f"test_jms_ParameterDefinitionTest"

    proj = Project(name=proj_name, active=True)
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    ip = IntParameterDefinition(name="int_param", upper_limit=27)
    sp = StringParameterDefinition(name="s_param", value_list=["l1", "l2"])
    ip = project_api.create_parameter_definitions([ip])[0]
    sp = project_api.create_parameter_definitions([sp])[0]

    for pd in [ip, sp]:
        assert pd.created_by is not missing
        assert pd.creation_time is not missing
        assert pd.modified_by is not missing
        assert pd.modification_time is not missing
        assert pd.created_by == pd.modified_by

    job_def = JobDefinition(name="New Config", active=True)
    job_def.parameter_definition_ids = [ip.id, sp.id]
    job_def = project_api.create_job_definitions([job_def])[0]
    assert len(job_def.parameter_definition_ids) == 2

    fp = FloatParameterDefinition(name="f_param", display_text="A Float Parameter")
    bp = BoolParameterDefinition(name="b_param", display_text="A Bool Parameter", default=False)
    fp = project_api.create_parameter_definitions([fp])[0]
    bp = project_api.create_parameter_definitions([bp])[0]
    job_def.parameter_definition_ids.extend([p.id for p in [bp, fp]])
    job_def = project_api.update_job_definitions([job_def])[0]
    assert len(job_def.parameter_definition_ids) == 4
    assert fp.id in job_def.parameter_definition_ids
    assert bp.id in job_def.parameter_definition_ids

    # Delete project
    jms_api.delete_project(proj)


def test_mixed_parameter_definition(client):

    proj_name = f"test_mixed_parameter_definition"

    proj = Project(name=proj_name, active=True)
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    ip = IntParameterDefinition(name="int_param", upper_limit=27)
    sp = StringParameterDefinition(name="s_param", value_list=["l1", "l2"])
    fp = FloatParameterDefinition(name="f_param", display_text="A Float Parameter")
    bp = BoolParameterDefinition(name="b_param", display_text="A Bool Parameter", default=False)

    original_pds = [ip, sp, fp, bp]
    pds = project_api.create_parameter_definitions(original_pds)

    for pd, original_pd in zip(pds, original_pds):
        assert type(pd) == type(original_pd)
        assert pd.name == original_pd.name

    assert pds[0].upper_limit == 27
    assert pds[1].value_list == ["l1", "l2"]

    # Delete project
    jms_api.delete_project(proj)
