import json
import logging
from typing import List, Type

from pydantic import BaseModel
from pydantic import __version__ as pydantic_version
from requests import Session

from ansys.rep.client.exceptions import ClientError

from ..models import (
    Cluster,
    ComputeResourceSet,
    EvaluatorConfigurationUpdate,
    EvaluatorRegistration,
    ScalerRegistration,
)

OBJECT_TYPE_TO_ENDPOINT = {
    Cluster: "clusters",
    EvaluatorRegistration: "evaluators",
    EvaluatorConfigurationUpdate: "configuration_updates",
    ScalerRegistration: "scalers",
    ComputeResourceSet: "compute_resource_sets",
}

log = logging.getLogger(__name__)


def object_to_dict(object: BaseModel, exclude_unset: bool = True, exclude_defaults: bool = False):
    if pydantic_version.startswith("1"):
        return object.dict(exclude_unset=exclude_unset, exclude_defaults=exclude_defaults)
    elif pydantic_version.startswith("2"):
        return object.model_dump(exclude_unset=exclude_unset, exclude_defaults=exclude_defaults)
    else:
        raise RuntimeError(f"Unsuppoorted Pydantic version {pydantic_version}")


def objects_to_json(
    objects: List[BaseModel],
    rest_name: str,
    exclude_unset: bool = True,
    exclude_defaults: bool = False,
):
    # Warning: this is a suboptimal way to serialize a list of objects to JSON.
    # Ideally, we'd like to use something similar to the marshmallow many=True option.
    # To achieve that, we could try to create a parent pydantic model at runtime.
    dicts = []
    for obj in objects:
        dicts.append(
            object_to_dict(obj, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults)
        )
    return json.dumps({rest_name: dicts})


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

    if objects is None:
        raise ClientError("objects can't be None")

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
