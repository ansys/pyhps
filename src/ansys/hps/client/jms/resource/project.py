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

# autogenerated code
from marshmallow.utils import missing
from ansys.hps.client.common import Object
from ..schema.project import ProjectSchema

class Project(Object):
    """Provides the project resource.

    Parameters
    ----------
    id : str
        Unique ID to access the project, assigned server side on creation.
    name : str
        Name of the project.
    active : bool
        Defines whether the project is active for evaluation.
    priority : int
        Priority for picking the project for evaluation.
    creation_time : datetime, optional
        Date and time that the project was created.
    modification_time : datetime, optional
        Date and time that the project was last modified.
    statistics : dict, optional
        Dictionary containing various project statistics.
    """

    class Meta:
        schema = ProjectSchema
        rest_name = "projects"

    def __init__(
        self,
        id=missing,
        name=missing,
        active=missing,
        priority=missing,
        creation_time=missing,
        modification_time=missing,
        statistics=missing,
        **kwargs
    ):
        self.id = id
        self.name = name
        self.active = active
        self.priority = priority
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.statistics = statistics

        self.obj_type = self.__class__.__name__


ProjectSchema.Meta.object_class = Project
