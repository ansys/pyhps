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

from collections import OrderedDict

from ansys.hps.client.jms.resource import TaskDefinition
from ansys.hps.client.jms.resource.task_definition import (
    HpcResources,
    Licensing,
    ResourceRequirements,
    SuccessCriteria,
)
from ansys.hps.client.jms.schema.task_definition import TaskDefinitionSchema


def test_task_definition_deserialization():

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
            "num_cores": 1,
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
            "hpc_resources": {
                "num_cores_per_node": 3,
                "exclusive": True,
                "queue": "myq",
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

    assert task_def.name == "test_task_def"
    assert task_def.execution_command == "echo 'hello world'"

    assert task_def.use_execution_script == False
    assert task_def.execution_script_id == None
    assert task_def.execution_level == 0
    assert task_def.execution_context == {
        "test_str": "5",
        "test_int": 1,
        "test_int2": 0,
        "test_float": 7.7,
        "test_bool": True,
        "test_bool2": False,
        "test_none": None,
    }
    assert task_def.environment == {"test_env": "test_env_value"}
    assert task_def.max_execution_time == 50
    assert task_def.num_trials == 1
    assert task_def.store_output == True
    assert task_def.input_file_ids == ["FAKE_FILE_ID"]
    assert task_def.output_file_ids == [
        "FAKE_FILE_ID",
        "FAKE_FILE_ID",
        "FAKE_FILE_ID",
    ]
    assert task_def.success_criteria == SuccessCriteria(
        return_code=0,
        require_all_output_files=False,
        require_all_output_parameters=True,
        expressions=[],
    )
    assert task_def.licensing == Licensing(enable_shared_licensing=False)
    assert task_def.software_requirements == []
    assert task_def.resource_requirements == ResourceRequirements(
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
        hpc_resources=HpcResources(exclusive=True, queue="myq", num_cores_per_node=3),
    )


def test_task_definition_serialization():

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
            hpc_resources=HpcResources(exclusive=True, num_gpus_per_node=2),
        ),
        software_requirements=[],
        store_output=True,
        success_criteria=SuccessCriteria(
            expressions=[],
            require_all_output_files=False,
            require_all_output_parameters=True,
            required_output_file_ids=["id1", "id2"],
            required_output_parameter_ids=["id3", "id4"],
            return_code=0,
        ),
        use_execution_script=False,
    )

    serialized_task_def = TaskDefinitionSchema().dump(task_def)

    assert serialized_task_def["name"] == "test_task_def"
    assert serialized_task_def["execution_command"] == "echo 'hello world'"

    assert serialized_task_def["use_execution_script"] == False
    assert serialized_task_def["execution_level"] == 0
    assert serialized_task_def["execution_context"] == {
        "test_str": "5",
        "test_int": 1,
        "test_int2": 0,
        "test_float": 7.7,
        "test_bool": True,
        "test_bool2": False,
        "test_none": None,
    }
    assert serialized_task_def["environment"] == {"test_env": "test_env_value"}
    assert serialized_task_def["max_execution_time"] == 50
    assert serialized_task_def["num_trials"] == 1
    assert serialized_task_def["store_output"] == True
    assert serialized_task_def["input_file_ids"] == ["FAKE_FILE_ID"]
    assert serialized_task_def["output_file_ids"] == [
        "FAKE_FILE_ID",
        "FAKE_FILE_ID",
        "FAKE_FILE_ID",
    ]
    assert serialized_task_def["success_criteria"] == OrderedDict(
        {
            "return_code": 0,
            "expressions": [],
            "required_output_file_ids": ["id1", "id2"],
            "require_all_output_files": False,
            "required_output_parameter_ids": ["id3", "id4"],
            "require_all_output_parameters": True,
        }
    )
    assert serialized_task_def["licensing"] == OrderedDict({"enable_shared_licensing": False})
    assert serialized_task_def["software_requirements"] == []
    assert serialized_task_def["resource_requirements"] == OrderedDict(
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
            "hpc_resources": {"num_gpus_per_node": 2, "exclusive": True},
        }
    )
