# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging
import sys
import unittest
import urllib.parse
from marshmallow.utils import missing

from ansys.rep.client.jms.resource import Project, JobDefinition
from ansys.rep.client.jms.resource.parameter_definition import (BoolParameterDefinition,
                                                                FloatParameterDefinition,
                                                                IntParameterDefinition,
                                                                StringParameterDefinition)
from ansys.rep.client.jms.schema.parameter_definition import (ParameterDefinitionSchema,
                                                              BoolParameterDefinitionSchema,
                                                              FloatParameterDefinitionSchema,
                                                              IntParameterDefinitionSchema,
                                                              StringParameterDefinitionSchema)
from test.rep_test import REPTestCase

log = logging.getLogger(__name__)


class ParameterDefitionTest(REPTestCase):
        
    def test_parameter_definition_deserialization(self):
        

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

        ip = IntParameterDefinitionSchema().load( int_parameter )
        self.assertEqual(ip.__class__.__name__, "IntParameterDefinition")
        self.assertEqual(ip.type, "int")
        self.assertEqual(ip.id, int_parameter["id"])
        self.assertEqual(ip.name, int_parameter["name"])
        self.assertEqual(ip.mode, "input")
        self.assertEqual(ip.cyclic, False)
        self.assertEqual(ip.upper_limit, 40)
        self.assertEqual(ip.quantity_name, int_parameter["quantity_name"])


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

        fp = FloatParameterDefinitionSchema().load( float_parameter )
        self.assertEqual(fp.__class__.__name__, "FloatParameterDefinition")
        self.assertEqual(fp.type, "float")
        self.assertEqual(fp.id, float_parameter["id"])
        self.assertEqual(fp.name, float_parameter["name"])
        self.assertEqual(fp.mode, "output")
        self.assertEqual(fp.step, None)
        self.assertEqual(fp.lower_limit, 0.5)
        self.assertEqual(fp.upper_limit, missing)
        self.assertEqual(fp.display_text, float_parameter["display_text"])
        self.assertEqual(fp.units, float_parameter["units"])

        string_parameter = {
            "default": "1",
            "quantity_name": None,
            "display_text": None,
            "mode": "input",
            "name": "tube4",
            "value_list": [
              "steel",
              "carbon",
              "resin"
            ],
            "id": "02q3Tt7pUwBe1GcX3WMYvs",
            "type": "string",
        }

        sp = StringParameterDefinitionSchema().load( string_parameter )
        self.assertEqual(sp.__class__.__name__, "StringParameterDefinition")
        self.assertEqual(sp.type, "string")
        self.assertEqual(sp.id, string_parameter["id"])
        self.assertEqual(sp.name, string_parameter["name"])
        self.assertEqual(sp.quantity_name, None)
        self.assertEqual(sp.value_list, ["steel", "carbon", "resin"])

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

        bp = BoolParameterDefinitionSchema().load( bool_parameter )
        self.assertEqual(bp.__class__.__name__, "BoolParameterDefinition")
        self.assertEqual(bp.type, "bool")
        self.assertEqual(bp.id, bool_parameter["id"])
        self.assertEqual(bp.name, bool_parameter["name"])
        self.assertEqual(bp.default, True)

        parameter_definitions = ParameterDefinitionSchema().load(
            [int_parameter, float_parameter, string_parameter, bool_parameter], many=True
        )
        self.assertEqual(parameter_definitions[0].__class__.__name__, "IntParameterDefinition")
        self.assertEqual(parameter_definitions[1].__class__.__name__, "FloatParameterDefinition")
        self.assertEqual(parameter_definitions[2].__class__.__name__, "StringParameterDefinition")
        self.assertEqual(parameter_definitions[3].__class__.__name__, "BoolParameterDefinition")

    def test_parameter_definition_serialization(self):

        ip = IntParameterDefinition(name="int_param", upper_limit=27, mode="input")

        self.assertEqual(ip.quantity_name, missing)
        self.assertEqual(ip.display_text, missing)
        self.assertEqual(ip.lower_limit, missing)
        self.assertEqual(ip.mode, "input")

        serialized_ip = IntParameterDefinitionSchema().dump(ip)

        self.assertFalse( "display_text" in serialized_ip.keys() )
        self.assertFalse( "lower_limit" in serialized_ip.keys() )
        self.assertEqual( serialized_ip["type"], "int" )
        self.assertEqual( serialized_ip["name"], "int_param" )
        self.assertEqual( serialized_ip["upper_limit"], 27 )
        self.assertFalse( "mode" in serialized_ip.keys() )

        sp = StringParameterDefinition(name="s_param", value_list=["l1", "l2"])
        serialized_sp = StringParameterDefinitionSchema().dump(sp)
        self.assertEqual( serialized_sp["type"], "string" )
        self.assertEqual( serialized_sp["value_list"], ["l1", "l2"] )

        serialized_param_defs = ParameterDefinitionSchema().dump([ip, sp], many=True)

        self.assertEqual( len(serialized_param_defs), 2 )
        self.assertFalse( "id" in serialized_param_defs[0].keys() )
        self.assertEqual( serialized_param_defs[0]["type"], "int" )
        self.assertEqual( serialized_param_defs[1]["type"], "string" )
        self.assertFalse( "display_text" in serialized_param_defs[0].keys() )
        self.assertEqual( serialized_param_defs[1]["name"], "s_param" )
        
        
    def test_parameter_definition_integration(self):

        client = self.jms_client()
        proj_name = f"test_jms_ParameterDefinitionTest_{self.run_id}"

        proj = Project(name=proj_name, active=True)
        proj = client.create_project(proj, replace=True)

        ip = IntParameterDefinition(name="int_param", upper_limit=27)
        sp = StringParameterDefinition(name="s_param", value_list=["l1", "l2"])
        ip = proj.create_parameter_definitions([ip])[0]
        sp = proj.create_parameter_definitions([sp])[0]

        job_def = JobDefinition(name="New Config", active=True)
        job_def.parameter_definition_ids = [ip.id, sp.id]
        job_def = proj.create_job_definitions([job_def])[0]
        self.assertEqual(len(job_def.parameter_definition_ids), 2)
        
        fp = FloatParameterDefinition(  name="f_param", display_name="A Float Parameter" )
        bp = BoolParameterDefinition(  name="b_param", display_name="A Bool Parameter", default=False )
        fp = proj.create_parameter_definitions([fp])[0]
        bp = proj.create_parameter_definitions([bp])[0]
        job_def.parameter_definition_ids.extend([p.id for p in [bp, fp]])
        job_def = proj.update_job_definitions([job_def])[0]
        self.assertEqual(len(job_def.parameter_definition_ids), 4)
        self.assertTrue(fp.id in job_def.parameter_definition_ids)
        self.assertTrue(bp.id in job_def.parameter_definition_ids)

        # job_def.parameter_definitions[2].upper_limit = 13.0
        # job_def.parameter_definitions[2].lower_limit = 4.5
        # job_def = proj.update_job_definitions([job_def])[0]
        # job_def = proj.get_job_definitions([job_def])[0]
        # self.assertEqual(len(job_def.parameter_definitions), 4)
        # self.assertEqual(job_def.parameter_definitions[2].upper_limit, 13.0)
        # self.assertEqual(job_def.parameter_definitions[2].lower_limit, 4.5)

        # Delete project
        client.delete_project(proj)

if __name__ == '__main__':
    unittest.main()
