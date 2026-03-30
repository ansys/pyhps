# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""A shared utility module."""

from pydantic import BaseModel
from pydantic import __version__ as pydantic_version


def _object_to_json(
    object: BaseModel,
    exclude_unset: bool = True,
    exclude_defaults: bool = False,
) -> str:
    """Convert a Pydantic object to a JSON string."""
    if pydantic_version.startswith("1."):
        return object.json(exclude_unset=exclude_unset, exclude_defaults=exclude_defaults)
    elif pydantic_version.startswith("2."):
        return object.model_dump_json(
            exclude_unset=exclude_unset, exclude_defaults=exclude_defaults
        )
    else:
        raise RuntimeError(f"Unsupported Pydantic version {pydantic_version}")


def _json_to_object(data, obj_type):
    return obj_type(**data)


def _json_to_objects(data, obj_type):
    obj_list = []
    for obj in data:
        obj_list.append(obj_type(**obj))
    return obj_list
