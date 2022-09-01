from ast import Str
import json
import logging
from typing import List

from requests import Session

from ansys.rep.client.exceptions import ClientError
from pydantic import BaseModel

from ..resource import (
    Job,
    JobDefinition,
    JobSelection,
    Project,
    Task,
    TaskDefinition,
    TaskDefinitionTemplate,
    Evaluator,
    BoolParameterDefinition,
    FloatParameterDefinition,
    IntParameterDefinition,
    StringParameterDefinition
)

OBJECT_TYPE_TO_ENDPOINT = [
    {Job : "jobs"},
    {JobDefinition, "job_definitions"},
    {Project, "projects"},
    {JobSelection: "job_selections"},
    {Task, "tasks"},
    {TaskDefinition, "task_definitions"},
    {BoolParameterDefinition, "parameter_definitions"},
    {FloatParameterDefinition, "parameter_definitions"},
    {IntParameterDefinition, "parameter_definitions"},
    {StringParameterDefinition, "parameter_definitions"}
]

log = logging.getLogger(__name__)

def objects_to_json(objects: List[BaseModel], rest_name: str):

    dicts = []
    for obj in objects:
        dicts.append(obj.dict())
    return json.dumps({rest_name: dicts})

def json_to_objects(data, obj_type):
    obj_list = []
    for obj in data:
        obj_list.append(obj_type(**obj)) 
    return obj_list

def get_objects(session: Session, url: str, obj_type, as_objects=True, **query_params):

    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]
    url = f"{url}/{rest_name}"
    query_params.setdefault("fields", "all")
    r = session.get(url, params=query_params)

    if query_params.get("count"):
        return r.json()[f"num_{rest_name}"]

    data = r.json()[rest_name]
    if not as_objects:
        return data

    return json_to_objects(data, obj_type)


def get_object(
    session: Session, url: str, obj_type, id: str, as_object=True, **query_params
):

    rest_name = OBJECT_TYPE_TO_ENDPOINT[obj_type]
    url = f"{url}/{rest_name}/{id}"
    query_params.setdefault("fields", "all")
    r = session.get(url, params=query_params)

    data = r.json()[rest_name]
    if not as_object:
        return data

    if len(data) == 0:
        return None
    elif len(data) == 1:
        return obj_type(**data)
    elif len(data) > 1:
        raise ClientError(
            f"Multiple objects with id={id}"
        )

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
    query_params.setdefault("fields", "all")

    r = session.post(f"{url}", data=objects_to_json(objects, rest_name), params=query_params)

    data = r.json()[rest_name]
    if not as_objects:
        return data
    return json_to_objects(data, obj_type)


def update_objects(
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
    query_params.setdefault("fields", "all")

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