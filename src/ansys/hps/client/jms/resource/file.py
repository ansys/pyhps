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
"""Module providing the file resource."""

import io
from datetime import datetime

from marshmallow.utils import missing

from ansys.hps.client.common import Object

from ..schema.file import FileSchema


class File(Object):
    """Provides the file resource.

    Parameters
    ----------
    src : Union[str, io.IOBase],  optional
        Client-only field to specify either the path of an input file
        or a file-like object. In the latter case, `requests` recommends that
        you open files in binary mode.
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    name : str
        Name of the file resource.
    type : str, optional
        Type of the file. While you can use any string, you should use the correct media type
        for the given resource.
    storage_id : str, optional
        ID of the file in the (orthogonal) file storage system.
    size : int, optional
    hash : str, optional
    creation_time : datetime, optional
        Date and time that the file resource was created.
    modification_time : datetime, optional
        Date and time that the file resource was last modified.
    created_by : str, optional
        ID of the user who created the object.
    modified_by : str, optional
        ID of the user who last modified the object.
    format : str, optional
    expiry_time : datetime, optional
        File expiration time.
    evaluation_path : str, optional
        Relative path for the file instance to store the job evaluation under.
    monitor : bool, optional
        Whether to live monitor the file's content.
    collect : bool, optional
        Whether the file should be collected per job.
    collect_interval : int, optional
        Collection frequency for a file with ``collect=True``. The minimum value
        is limited by the evaluator's settings. A value of ``0`` or ``None`` indicates
        that the evaluator should decide. Another value indicates the interval in seconds.
    reference_id : str, optional
        ID of the reference file that this file was created from.

    """

    class Meta:
        schema = FileSchema
        rest_name = "files"

    def __init__(
        self,
        src: str | io.IOBase = None,
        id: str = missing,
        creation_time: datetime = missing,
        modification_time: datetime = missing,
        created_by: str = missing,
        modified_by: str = missing,
        name: str = missing,
        type: str = missing,
        storage_id: str = missing,
        size: int = missing,
        hash: str = missing,
        expiry_time: datetime = missing,
        format: str = missing,
        evaluation_path: str = missing,
        monitor: bool = missing,
        collect: bool = missing,
        collect_interval: int = missing,
        reference_id: str = missing,
        **kwargs,
    ):
        self.src = src
        self.content = None

        self.id = id
        self.name = name
        self.type = type
        self.storage_id = storage_id
        self.size = size
        self.hash = hash
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.created_by = created_by
        self.modified_by = modified_by
        self.expiry_time = expiry_time
        self.format = format
        self.evaluation_path = evaluation_path
        self.monitor = monitor
        self.collect = collect
        self.collect_interval = collect_interval
        self.reference_id = reference_id

        self.obj_type = self.__class__.__name__


FileSchema.Meta.object_class = File
