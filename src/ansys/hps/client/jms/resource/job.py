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

# DO NOT EDIT.
# This file is automatically generated from the JMS schemas.

"""Module providing the job resource."""
from datetime import datetime

from ansys.hps.client.common import Object
from marshmallow.utils import missing

from ..schema.job import JobSchema


class Job(Object):
    """Provides the job resource.

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
    name : str, optional
        Name of the job.
    eval_status : str
        Evaluation status.
    job_definition_id : str
        ID of the linked job definition. For more information, see the :class:`JobDefinition` class.
    priority : int, optional
        Priority for evaluating the job. The default is ``0``, which is the highest priority. Assigning a higher value to a job makes it a lower priority.
    values : dict[str, any], optional
        Dictionary with (name,value) pairs for all parameters defined in the linked job definition.
    fitness : float, optional
        Fitness value computed.
    fitness_term_values : dict[str, float], optional
        Dictionary with (name,value) pairs for all fitness terms computed.
    note : str, optional
        Note for the job.
    creator : str, optional
        Additional information about the creator of the job.
    executed_level : int, optional
        Execution level of the last executed task. A value of ``-1`` indicates that no task has been executed yet.
    elapsed_time : float
        Number of seconds it took the evaluators to update the job.
    host_ids : list, optional
        List of host IDs of the evaluators that updated the job.
    file_ids : list[str]
        List of IDs of all files of the job.
    """

    class Meta:
        schema = JobSchema
        rest_name = "jobs"

    def __init__(
        self,
        id: str = missing,
        creation_time: datetime = missing,
        modification_time: datetime = missing,
        created_by: str = missing,
        modified_by: str = missing,
        name: str = missing,
        eval_status: str = missing,
        job_definition_id: str = missing,
        priority: int = missing,
        values: dict[str, any] = missing,
        fitness: float = missing,
        fitness_term_values: dict[str, float] = missing,
        note: str = missing,
        creator: str = missing,
        executed_level: int = missing,
        elapsed_time: float = missing,
        host_ids: list = missing,
        file_ids: list[str] = missing,
        **kwargs,
    ):
        self.id = id
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.name = name
        self.eval_status = eval_status
        self.job_definition_id = job_definition_id
        self.priority = priority
        self.values = values
        self.fitness = fitness
        self.fitness_term_values = fitness_term_values
        self.note = note
        self.creator = creator
        self.executed_level = executed_level
        self.elapsed_time = elapsed_time
        self.host_ids = host_ids
        self.file_ids = file_ids

        self.obj_type = self.__class__.__name__


JobSchema.Meta.object_class = Job
