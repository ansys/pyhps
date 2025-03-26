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
"""Module creating, getting, updating, deleting and copying objects."""

import json
import logging

from requests import Session

from ansys.hps.client.common import Object
from ansys.hps.client.exceptions import ClientError

log = logging.getLogger(__name__)


def get_objects(
    session: Session, url: str, obj_type: type[Object], as_objects=True, **query_params
):
    """Get objects with a session, URL, and object type."""
    rest_name = obj_type.Meta.rest_name
    url = f"{url}/{rest_name}"
    r = session.get(url, params=query_params)

    if query_params.get("count"):
        return r.json()[f"num_{rest_name}"]

    data = r.json()[rest_name]
    if not as_objects:
        return data

    schema = obj_type.Meta.schema(many=True)
    return schema.load(data)


def get_object(
    session: Session, url: str, obj_type: type[Object], id: str, as_object=True, **query_params
):
    """Get an object with a session, URL, object type, and object."""
    rest_name = obj_type.Meta.rest_name
    url = f"{url}/{rest_name}/{id}"
    r = session.get(url, params=query_params)

    data = r.json()[rest_name]
    if not as_object:
        return data

    schema = obj_type.Meta.schema(many=True)
    if len(data) == 0:
        return None
    elif len(data) == 1:
        return schema.load(data)[0]
    elif len(data) > 1:
        raise ClientError(
            f"Multiple {Object.__class__.__name__} objects with id={id}: {schema.load(data)}"
        )


def _check_object_types(objects: list[Object], obj_type: type[Object]):
    """Check object types."""
    are_same = [isinstance(o, obj_type) for o in objects]
    if not all(are_same):
        actual_types = {type(o) for o in objects}
        if len(actual_types) == 1:
            actual_types = actual_types.pop()
        raise ClientError(f"Wrong object types: expected '{obj_type}', got {actual_types}.")


def create_objects(
    session: Session,
    url: str,
    objects: list[Object],
    obj_type: type[Object],
    as_objects=True,
    **query_params,
):
    """Create objects."""
    if not objects:
        return []

    _check_object_types(objects, obj_type)

    rest_name = obj_type.Meta.rest_name

    url = f"{url}/{rest_name}"
    schema = obj_type.Meta.schema(many=True)
    serialized_data = schema.dump(objects)
    json_data = json.dumps({rest_name: serialized_data})

    r = session.post(f"{url}", data=json_data, params=query_params)
    data = r.json()[rest_name]
    if not as_objects:
        return data

    return schema.load(data)


def update_objects(
    session: Session,
    url: str,
    objects: list[Object],
    obj_type: type[Object],
    as_objects=True,
    **query_params,
):
    """Update objects."""
    if not objects:
        return []

    _check_object_types(objects, obj_type)

    rest_name = obj_type.Meta.rest_name

    url = f"{url}/{rest_name}"
    schema = obj_type.Meta.schema(many=True)
    serialized_data = schema.dump(objects)
    json_data = json.dumps({rest_name: serialized_data})
    r = session.put(f"{url}", data=json_data, params=query_params)

    data = r.json()[rest_name]
    if not as_objects:
        return data

    return schema.load(data)


def delete_objects(session: Session, url: str, objects: list[Object], obj_type: type[Object]):
    """Delete objects."""
    if not objects:
        return

    _check_object_types(objects, obj_type)

    obj_type = objects[0].__class__
    rest_name = obj_type.Meta.rest_name
    url = f"{url}/{rest_name}"
    data = json.dumps({"source_ids": [obj.id for obj in objects]})

    _ = session.delete(url, data=data)


def copy_objects(session: Session, url: str, objects: list[Object], wait: bool = True) -> str:
    """Copy objects."""
    are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
    if not all(are_same):
        raise ClientError("Mixed object types")

    obj_type = objects[0].__class__
    rest_name = obj_type.Meta.rest_name
    url = f"{url}/{rest_name}:copy"

    source_ids = [obj.id for obj in objects]
    r = session.post(url, data=json.dumps({"source_ids": source_ids}))

    operation_location = r.headers["location"]
    operation_id = operation_location.rsplit("/", 1)[-1]

    return operation_id
