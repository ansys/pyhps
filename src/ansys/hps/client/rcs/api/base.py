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
from requests import Session

from ansys.hps.client.common.utils import _json_to_object, _object_to_json

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


def create_object(session: Session, url: str, object: BaseModel, as_object=True):
    """Create an object and return the response as an object or a dictionary."""
    if not object:
        return []

    obj_type = object.__class__
    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]

    url = f"{url}/{rest_name}"
    r = session.post(f"{url}", data=_object_to_json(object))

    data = r.json()
    if not as_object:
        return data
    obj_type = OBJECT_TYPE_TO_RESPONSE_MODEL[obj_type]
    return _json_to_object(data, obj_type)


def delete_object(session: Session, url: str, object: BaseModel, as_object=True):
    """Delete an object and return the response as an object or a dictionary."""
    if not object:
        return

    obj_type = object.__class__
    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]

    url = f"{url}/{rest_name}"

    r = session.delete(url, data=_object_to_json(object))

    data = r.json()

    if not as_object:
        return data
    obj_type = OBJECT_TYPE_TO_RESPONSE_MODEL[obj_type]
    return _json_to_object(data, obj_type)
