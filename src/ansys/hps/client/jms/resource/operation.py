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

from ..schema.operation import OperationSchema


class Operation(Object):
    """Operation resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    name : str, optional
    target : list, optional
    finished : bool, optional
    succeeded : bool, optional
    progress : float, optional
    status : str, optional
    result : dict, optional
    messages : list, optional
    start_time : datetime, optional
    end_time : datetime, optional

    """

    class Meta:
        schema = OperationSchema
        rest_name = "operations"

    def __init__(
        self,
        id=missing,
        name=missing,
        target=missing,
        finished=missing,
        succeeded=missing,
        progress=missing,
        status=missing,
        result=missing,
        messages=missing,
        start_time=missing,
        end_time=missing,
        **kwargs
    ):
        self.id = id
        self.name = name
        self.target = target
        self.finished = finished
        self.succeeded = succeeded
        self.progress = progress
        self.status = status
        self.result = result
        self.messages = messages
        self.start_time = start_time
        self.end_time = end_time

        self.obj_type = self.__class__.__name__


OperationSchema.Meta.object_class = Operation
