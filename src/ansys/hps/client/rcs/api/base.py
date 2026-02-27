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
"""Utilities to convert objects to and from JSON."""

import logging

from pydantic import BaseModel
from pydantic import __version__ as pydantic_version
from requests import Session

from ..models import (
    RegisterInstance,
    RegisterInstanceResponse,
    UnRegisterInstance,
    UnRegisterInstanceResponse,
)

OBJECT_TYPE_TO_ENDPOINT = {
    RegisterInstance: "register_instance",
    UnRegisterInstance: "unregister_instance",
}
OBJECT_TYPE_TO_RESPONSE_MODEL = {
    RegisterInstance: RegisterInstanceResponse,
    UnRegisterInstance: UnRegisterInstanceResponse,
}

log = logging.getLogger(__name__)


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


def create_objects(session: Session, url: str, object: BaseModel, as_objects=True):
    """Create a list of objects."""
    if not object:
        return []

    obj_type = object.__class__
    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]

    url = f"{url}/{rest_name}"
    r = session.post(f"{url}", data=_object_to_json(object))

    data = r.json()
    if not as_objects:
        return data
    obj_type = OBJECT_TYPE_TO_RESPONSE_MODEL[obj_type]
    return _json_to_object(data, obj_type)


def delete_objects(session: Session, url: str, object: BaseModel, as_objects=True):
    """Delete a list of objects."""
    if not object:
        return

    obj_type = object.__class__
    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]

    url = f"{url}/{rest_name}"

    r = session.delete(url, data=_object_to_json(object))

    data = r.json()

    if not as_objects:
        return data
    obj_type = OBJECT_TYPE_TO_RESPONSE_MODEL[obj_type]
    return _json_to_object(data, obj_type)
