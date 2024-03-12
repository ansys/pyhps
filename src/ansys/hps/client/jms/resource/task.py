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

# autogenerated code
"""Module providing the task resource."""
from datetime import datetime
from typing import Any, Dict, List, Union

from marshmallow.utils import missing

from ansys.hps.client.common import Object

from ..schema.task import TaskSchema
from .task_definition import TaskDefinition


class Task(Object):
    """Provides the task resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    creation_time : datetime, optional
        Date and time that the resource was created.
    modification_time : datetime, optional
        Date and time that the resource was last modified.
    created_by : str, optional
        ID of the user who created the object.
    modified_by : str, optional
        ID of the user who last modified the object.
    pending_time : datetime, optional
        Date and time that the task was set to pending.
    prolog_time : datetime, optional
        Date and time that the task was set to prolog.
    running_time : datetime, optional
        Date and time that the task was set to running.
    finished_time : datetime, optional
        Date and time that the task was completed.
    eval_status : str, optional
        Evaluation status.
    trial_number : int, optional
        Which attempt to execute the process step this task represents.
    elapsed_time : float, optional
        Number of seconds it took the evaluator to execute the task.
    task_definition_id : str
        ID of the :class:`TaskDefinition` instance that the task is linked to.
    task_definition_snapshot : TaskDefinition, optional
        Snapshot of the  :class:`TaskDefinition` instance that was created when the task status changed to prolog, before evaluation.
    executed_command : str, optional
    job_id : str
        ID of the :class:`Job` instance that the task is linked to.
    host_id : str, optional
        UUID of the :class:`Evaluator` instance that updated the task.
    input_file_ids : list[str]
        List of IDs of input files of the task.
    output_file_ids : list[str]
        List of IDs of output files of the task.
    monitored_file_ids : list[str]
        List of IDs of monitored files of the task.
    inherited_file_ids : list[str]
        List of IDs of inherited files of the task.
    owned_file_ids : list[str]
        List of IDs of owned files of the task.
    license_context_id : str, optional
        ID of the license context in use.
    custom_data : dict, optional
        Dictionary type field for storing custom data.
    working_directory : str, optional
        Working directory of the task.
    """

    class Meta:
        schema = TaskSchema
        rest_name = "tasks"

    def __init__(
        self,
        id: str = missing,
        creation_time: datetime = missing,
        modification_time: datetime = missing,
        created_by: str = missing,
        modified_by: str = missing,
        pending_time: datetime = missing,
        prolog_time: datetime = missing,
        running_time: datetime = missing,
        finished_time: datetime = missing,
        eval_status: str = missing,
        trial_number: int = missing,
        elapsed_time: float = missing,
        task_definition_id: str = missing,
        task_definition_snapshot: TaskDefinition = missing,
        executed_command: str = missing,
        job_id: str = missing,
        host_id: str = missing,
        input_file_ids: List[str] = missing,
        output_file_ids: List[str] = missing,
        monitored_file_ids: List[str] = missing,
        inherited_file_ids: List[str] = missing,
        owned_file_ids: List[str] = missing,
        license_context_id: str = missing,
        custom_data: Dict = missing,
        working_directory: str = missing,
        **kwargs
    ):
        self.id = id
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.pending_time = pending_time
        self.prolog_time = prolog_time
        self.running_time = running_time
        self.finished_time = finished_time
        self.eval_status = eval_status
        self.trial_number = trial_number
        self.elapsed_time = elapsed_time
        self.task_definition_id = task_definition_id
        self.task_definition_snapshot = task_definition_snapshot
        self.executed_command = executed_command
        self.job_id = job_id
        self.host_id = host_id
        self.input_file_ids = input_file_ids
        self.output_file_ids = output_file_ids
        self.monitored_file_ids = monitored_file_ids
        self.inherited_file_ids = inherited_file_ids
        self.owned_file_ids = owned_file_ids
        self.license_context_id = license_context_id
        self.custom_data = custom_data
        self.working_directory = working_directory

        self.obj_type = self.__class__.__name__


TaskSchema.Meta.object_class = Task
