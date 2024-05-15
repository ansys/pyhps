# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

import io
import logging

import pytest

from ansys.hps.client import ClientError
from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import (
    File,
    Job,
    JobDefinition,
    Project,
    Software,
    TaskCommand,
    TaskCommandDefinition,
    TaskDefinition,
)

log = logging.getLogger(__name__)

EXECUTION_SCRIPT = """
import os
from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution

class MyApplicationExecution(ApplicationExecution):
    class Meta(ApplicationExecution.Meta):
        available_commands = ["my_command"]

    def my_command(self, arg1: float, arg2: str):
        log.info("start my_command")
        with open("command.out", "w") as file:
            file.write("output of my_command")
        log.info("end my_command")

    def execute(self):
        log.info("My execution script")
"""


def test_job_with_commands(client):

    jms_api = JmsApi(client)
    proj_name = f"test_job_with_commands"
    proj = Project(name=proj_name)
    proj = jms_api.create_project(proj)
    project_api = ProjectApi(client, proj.id)
    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    exec_script = File(
        name="exec_script",
        evaluation_path="exec_script.py",
        type="application/x-python-code",
        src=io.StringIO(EXECUTION_SCRIPT),
    )
    exec_script = project_api.create_files([exec_script])[0]

    task_def = TaskDefinition(
        name="Test",
        software_requirements=[
            Software(name="Ansys Python", version="2024 R2 Python 3.10"),
        ],
        execution_level=0,
        store_output=True,
        use_execution_script=True,
        execution_script_id=exec_script.id,
    )

    task_def = project_api.create_task_definitions([task_def])[0]

    # !! WORKAROUND TO LET THE TEST TEMPORARILY PASS !!
    task_def = project_api.update_task_definitions([task_def])[0]

    command_definitions = project_api.get_task_command_definitions(task_definition_id=task_def.id)
    assert len(command_definitions) == 1
    for cd in command_definitions:
        assert isinstance(cd, TaskCommandDefinition)
        assert cd.name == "my_command"
        assert len(cd.parameters) == 2
        assert cd.parameters["arg1"] == "float"
        assert cd.parameters["arg2"] == "str"

    job_def = JobDefinition(name="JobDefinition", active=True)
    job_def.task_definition_ids = [task_def.id]
    job_def = project_api.create_job_definitions([job_def])[0]

    job = Job(
        name=f"Test Job",
        eval_status="pending",
        job_definition_id=job_def.id,
    )
    job = project_api.create_jobs([job])[0]

    task = project_api.get_tasks()[0]

    # verify error on wrong command name
    with pytest.raises(ClientError) as ex_info:
        _ = project_api.queue_task_command(task.id, "wrong_command_name", arg1=6.5, arg2="test")
    assert "Could not find a command named 'wrong_command_name'" in str(ex_info.value)

    # verify error on wrong command arguments
    with pytest.raises(ClientError) as ex_info:
        _ = project_api.queue_task_command(task.id, "my_command", arg1=6.5)
    assert "matching arguments" in str(ex_info.value)

    with pytest.raises(ClientError) as ex_info:
        _ = project_api.queue_task_command(task.id, "my_command", arg_wrong=6.5)
    assert "matching arguments" in str(ex_info.value)

    # verify sending correct command
    command = project_api.queue_task_command(task.id, "my_command", arg1=6.5, arg2="test")

    assert isinstance(command, TaskCommand)
    assert command.arguments["arg1"] == 6.5
    assert command.arguments["arg2"] == "test"
    assert command.status == "new"

    # verify get commands
    commands = project_api.get_task_commands(task_id=task.id)
    assert len(commands) == 1
    assert commands[0].status == "new"

    JmsApi(client).delete_project(proj)
