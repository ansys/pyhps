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

# DO NOT EDIT.
# This file is automatically generated from the JMS schemas.

"""Module providing the algorithm resource."""
from datetime import datetime
from typing import Any, Dict, List, Union

from marshmallow.utils import missing

from ansys.hps.client.common import Object

from ..schema.algorithm import AlgorithmSchema


class Algorithm(Object):
    """Provides the algorithm resource.

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
        Name of the algorithm.
    description : str, optional
        Description of the algorithm.
    data : str, optional
        Generic string field to hold arbitrary algorithm configuration data. For example, as a JSON dictionary.
    jobs : list[str]
        List of job IDs.
    """

    class Meta:
        schema = AlgorithmSchema
        rest_name = "algorithms"

    def __init__(
        self,
        id: str = missing,
        creation_time: datetime = missing,
        modification_time: datetime = missing,
        created_by: str = missing,
        modified_by: str = missing,
        name: str = missing,
        description: str = missing,
        data: str = missing,
        jobs: List[str] = missing,
        **kwargs,
    ):
        self.id = id
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.name = name
        self.description = description
        self.data = data
        self.jobs = jobs

        self.obj_type = self.__class__.__name__


AlgorithmSchema.Meta.object_class = Algorithm
