import json
import logging
from typing import List, Type

from pydantic import BaseModel
from requests import Session

from ansys.rep.client.exceptions import ClientError

from ..models import EvaluatorConfiguration, EvaluatorConfigurationUpdate, EvaluatorRegistration

OBJECT_TYPE_TO_ENDPOINT = {
    EvaluatorRegistration: "evaluators",
    EvaluatorConfiguration: "configuration",
    EvaluatorConfigurationUpdate: "configurtion_updates",
}

log = logging.getLogger(__name__)


def objects_to_json(objects: List[BaseModel], rest_name: str):

    dicts = []
    for obj in objects:
        dicts.append(obj.model_dump_json())
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

    # todo rms
    if query_params.get("count"):
        return r.json()[f"num_{rest_name}"]

    data = r.json()[rest_name]
    if not as_objects:
        return data

    return json_to_objects(data, obj_type)


def get_object(
    session: Session, url: str, obj_type: Type[BaseModel], id: str, as_object=True, **query_params
):

    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]
    url = f"{url}/{rest_name}/{id}"
    r = session.get(url, params=query_params)

    data = r.json()[rest_name]
    if not as_object:
        return data

    if len(data) == 0:
        return None
    elif len(data) == 1:
        return obj_type(**data)
    elif len(data) > 1:
        raise ClientError(f"Multiple objects with id={id}")


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
