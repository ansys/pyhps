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
"""Module getting, updating, creating, and deleting objects, and converting objects
to and from JSONs."""
import json
import logging
from typing import List, Type

from pydantic import BaseModel
from pydantic import __version__ as pydantic_version
from pydantic import create_model
from requests import Session

from ansys.hps.client.exceptions import ClientError

from ..models import (
    ComputeResourceSet,
    EvaluatorConfigurationUpdate,
    EvaluatorRegistration,
    ScalerRegistration,
)

OBJECT_TYPE_TO_ENDPOINT = {
    EvaluatorRegistration: "evaluators",
    EvaluatorConfigurationUpdate: "configuration_updates",
    ScalerRegistration: "scalers",
    ComputeResourceSet: "compute_resource_sets",
}

log = logging.getLogger(__name__)


def _create_dynamic_list_model(name, field_name, field_type) -> BaseModel:
    # Helper function to create at runtime a pydantic model storing
    # a list of objects.
    fields = {f"{field_name}": (List[field_type], ...)}
    return create_model(name, **fields)


def objects_to_json(
    objects: List[BaseModel],
    rest_name: str,
    exclude_unset: bool = True,
    exclude_defaults: bool = False,
):

    ListOfObjects = _create_dynamic_list_model(
        name=f"List{objects[0].__class__.__name__}",
        field_name=rest_name,
        field_type=objects[0].__class__,
    )

    args = {f"{rest_name}": objects}
    objects_list = ListOfObjects(**args)

    if pydantic_version.startswith("1."):
        return objects_list.json(exclude_unset=exclude_unset, exclude_defaults=exclude_defaults)
    elif pydantic_version.startswith("2."):
        return objects_list.model_dump_json(
            exclude_unset=exclude_unset, exclude_defaults=exclude_defaults
        )
    else:
        raise RuntimeError(f"Unsupported Pydantic version {pydantic_version}")


def json_to_objects(data, obj_type):
    obj_list = []
    for obj in data:
        obj_list.append(obj_type(**obj))
    return obj_list


def get_objects(
    session: Session, url: str, obj_type: Type[BaseModel], as_objects=True, **query_params
):

    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]
    url = f"{url}/{rest_name}"
    r = session.get(url, params=query_params)

    data = r.json()[rest_name]
    if not as_objects:
        return data

    return json_to_objects(data, obj_type)


def get_objects_count(session: Session, url: str, obj_type: Type[BaseModel], **query_params):

    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]
    url = f"{url}/{rest_name}:count"  # noqa: E231
    r = session.get(url, params=query_params)

    return r.json()[f"num_{rest_name}"]


def get_object(
    session: Session,
    url: str,
    obj_type: Type[BaseModel],
    as_object=True,
    from_collection=False,
    **query_params,
):

    r = session.get(url, params=query_params)
    data = r.json()
    if from_collection:
        rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]
        data = data[rest_name][0]
    if not as_object:
        return data
    return obj_type(**data)


def create_objects(
    session: Session, url: str, objects: List[BaseModel], as_objects=True, **query_params
):
    if not objects:
        return []

    are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
    if not all(are_same):
        raise ClientError("Mixed object types")

    obj_type = objects[0].__class__
    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]

    url = f"{url}/{rest_name}"

    r = session.post(f"{url}", data=objects_to_json(objects, rest_name), params=query_params)

    data = r.json()[rest_name]
    if not as_objects:
        return data

    return json_to_objects(data, obj_type)


def update_objects(
    session: Session,
    url: str,
    objects: List[BaseModel],
    obj_type: Type[BaseModel],
    as_objects=True,
    **query_params,
):

    if not objects:
        return []

    are_same = [o.__class__ == obj_type for o in objects]
    if not all(are_same):
        raise ClientError("Mixed object types")

    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]

    url = f"{url}/{rest_name}"

    r = session.put(f"{url}", data=objects_to_json(objects, rest_name), params=query_params)

    data = r.json()[rest_name]
    if not as_objects:
        return data

    return json_to_objects(data, obj_type)


def delete_objects(session: Session, url: str, objects: List[BaseModel]):
    if not objects:
        return

    are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
    if not all(are_same):
        raise ClientError("Mixed object types")

    obj_type = objects[0].__class__
    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]

    url = f"{url}/{rest_name}"
    data = json.dumps({"source_ids": [obj.id for obj in objects]})

    r = session.delete(url, data=data)
