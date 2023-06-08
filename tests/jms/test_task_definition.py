from collections import OrderedDict
import unittest

from ansys.rep.client.jms.resource import TaskDefinition
from ansys.rep.client.jms.resource.task_definition import (
    Licensing,
    ResourceRequirements,
    SuccessCriteria,
)
from ansys.rep.client.jms.schema.task_definition import TaskDefinitionSchema
from tests.rep_test import REPTestCase


class TaskDefinitionTest(REPTestCase):
    def test_task_definition_deserialization(self):

        task_def_dict = {
            "environment": {"test_env": "test_env_value"},
            "execution_command": "echo 'hello world'",
            "execution_context": {
                "test_str": "5",
                "test_int": 1,
                "test_int2": 0,
                "test_float": 7.7,
                "test_bool": True,
                "test_bool2": False,
                "test_none": None,
            },
            "execution_level": 0,
            "execution_script_id": None,
            "id": "1",
            "licensing": {"enable_shared_licensing": False},
            "max_execution_time": 50,
            "name": "test_task_def",
            "num_trials": 1,
            "input_file_ids": ["FAKE_FILE_ID"],
            "output_file_ids": [
                "FAKE_FILE_ID",
                "FAKE_FILE_ID",
                "FAKE_FILE_ID",
            ],
            "resource_requirements": {
                "cpu_core_usage": 1,
                "disk_space": 5,
                "memory": 250,
                "custom": {
                    "test_str": "5",
                    "test_int": 1,
                    "test_int2": 0,
                    "test_float": 7.7,
                    "test_bool": True,
                    "test_bool2": False,
                    "test_none": None,
                },
            },
            "software_requirements": [],
            "store_output": True,
            "success_criteria": {
                "expressions": [],
                "require_all_output_files": False,
                "require_all_output_parameters": True,
                "return_code": 0,
            },
            "use_execution_script": False,
        }

        task_def = TaskDefinitionSchema().load(task_def_dict)

        self.assertEqual(task_def.name, "test_task_def")
        self.assertEqual(task_def.execution_command, "echo 'hello world'")

        self.assertEqual(task_def.use_execution_script, False)
        self.assertEqual(task_def.execution_script_id, None)
        self.assertEqual(task_def.execution_level, 0)
        self.assertEqual(
            task_def.execution_context,
            {
                "test_str": "5",
                "test_int": 1,
                "test_int2": 0,
                "test_float": 7.7,
                "test_bool": True,
                "test_bool2": False,
                "test_none": None,
            },
        )
        self.assertEqual(task_def.environment, {"test_env": "test_env_value"})
        self.assertEqual(task_def.max_execution_time, 50)
        self.assertEqual(task_def.num_trials, 1)
        self.assertEqual(task_def.store_output, True)
        self.assertEqual(task_def.input_file_ids, ["FAKE_FILE_ID"])
        self.assertEqual(
            task_def.output_file_ids,
            [
                "FAKE_FILE_ID",
                "FAKE_FILE_ID",
                "FAKE_FILE_ID",
            ],
        )
        self.assertEqual(
            task_def.success_criteria,
            SuccessCriteria(
                return_code=0,
                require_all_output_files=False,
                require_all_output_parameters=True,
                expressions=[],
            ),
        )
        self.assertEqual(task_def.licensing, Licensing(enable_shared_licensing=False))
        self.assertEqual(task_def.software_requirements, [])
        self.assertEqual(
            task_def.resource_requirements,
            ResourceRequirements(
                num_cores=1,
                disk_space=5,
                memory=250,
                custom={
                    "test_str": "5",
                    "test_int": 1,
                    "test_int2": 0,
                    "test_float": 7.7,
                    "test_bool": True,
                    "test_bool2": False,
                    "test_none": None,
                },
            ),
        )

    def test_task_definition_serialization(self):

        task_def = TaskDefinition(
            name="test_task_def",
            environment={"test_env": "test_env_value"},
            execution_command="echo 'hello world'",
            execution_context={
                "test_str": "5",
                "test_int": 1,
                "test_int2": 0,
                "test_float": 7.7,
                "test_bool": True,
                "test_bool2": False,
                "test_none": None,
            },
            execution_level=0,
            id=1,
            licensing=Licensing(enable_shared_licensing=False),
            max_execution_time=50,
            num_trials=1,
            input_file_ids=["FAKE_FILE_ID"],
            output_file_ids=["FAKE_FILE_ID", "FAKE_FILE_ID", "FAKE_FILE_ID"],
            resource_requirements=ResourceRequirements(
                num_cores=1,
                disk_space=5,
                memory=250,
                custom={
                    "test_str": "5",
                    "test_int": 1,
                    "test_int2": 0,
                    "test_float": 7.7,
                    "test_bool": True,
                    "test_bool2": False,
                    "test_none": None,
                },
            ),
            software_requirements=[],
            store_output=True,
            success_criteria=SuccessCriteria(
                expressions=[],
                require_all_output_files=False,
                require_all_output_parameters=True,
                return_code=0,
            ),
            use_execution_script=False,
        )

        serialized_task_def = TaskDefinitionSchema().dump(task_def)

        self.assertEqual(serialized_task_def["name"], "test_task_def")
        self.assertEqual(serialized_task_def["execution_command"], "echo 'hello world'")

        self.assertEqual(serialized_task_def["use_execution_script"], False)
        self.assertEqual(serialized_task_def["execution_level"], 0)
        self.assertEqual(
            serialized_task_def["execution_context"],
            {
                "test_str": "5",
                "test_int": 1,
                "test_int2": 0,
                "test_float": 7.7,
                "test_bool": True,
                "test_bool2": False,
                "test_none": None,
            },
        )
        self.assertEqual(serialized_task_def["environment"], {"test_env": "test_env_value"})
        self.assertEqual(serialized_task_def["max_execution_time"], 50)
        self.assertEqual(serialized_task_def["num_trials"], 1)
        self.assertEqual(serialized_task_def["store_output"], True)
        self.assertEqual(serialized_task_def["input_file_ids"], ["FAKE_FILE_ID"])
        self.assertEqual(
            serialized_task_def["output_file_ids"],
            [
                "FAKE_FILE_ID",
                "FAKE_FILE_ID",
                "FAKE_FILE_ID",
            ],
        )
        self.assertEqual(
            serialized_task_def["success_criteria"],
            OrderedDict(
                {
                    "return_code": 0,
                    "expressions": [],
                    "require_all_output_files": False,
                    "require_all_output_parameters": True,
                }
            ),
        )
        self.assertEqual(
            serialized_task_def["licensing"], OrderedDict({"enable_shared_licensing": False})
        )
        self.assertEqual(serialized_task_def["software_requirements"], [])
        self.assertEqual(
            serialized_task_def["resource_requirements"],
            OrderedDict(
                {
                    "memory": 250,
                    "num_cores": 1,
                    "disk_space": 5,
                    "custom": {
                        "test_str": "5",
                        "test_int": 1,
                        "test_int2": 0,
                        "test_float": 7.7,
                        "test_bool": True,
                        "test_bool2": False,
                        "test_none": None,
                    },
                }
            ),
        )


if __name__ == "__main__":
    unittest.main()
