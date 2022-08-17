import json
import logging
from typing import List

from requests import Session

from ansys.rep.client.exceptions import ClientError

from ..resource.base import Object

log = logging.getLogger(__name__)


def get_objects(session: Session, url: str, obj_type: Object, as_objects=True, **query_params):

    rest_name = obj_type.Meta.rest_name
    url = f"{url}/{rest_name}"
    query_params.setdefault("fields", "all")
    r = session.get(url, params=query_params)

    if query_params.get("count"):
        return r.json()[f"num_{rest_name}"]

    data = r.json()[rest_name]
    if not as_objects:
        return data

    schema = obj_type.Meta.schema(many=True)
    return schema.load(data)


def create_objects(
    session: Session, url: str, objects: List[Object], as_objects=True, **query_params
):
    if not objects:
        return []

    are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
    if not all(are_same):
        raise ClientError("Mixed object types")

    obj_type = objects[0].__class__
    rest_name = obj_type.Meta.rest_name

    url = f"{url}/{rest_name}"
    query_params.setdefault("fields", "all")
    schema = obj_type.Meta.schema(many=True)
    serialized_data = schema.dump(objects)
    json_data = json.dumps({rest_name: serialized_data})

    r = session.post(f"{url}", data=json_data, params=query_params)
    data = r.json()[rest_name]
    if not as_objects:
        return data

    return schema.load(data)


def update_objects(
    session: Session, url: str, objects: List[Object], as_objects=True, **query_params
):
    if not objects:
        return []

    are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
    if not all(are_same):
        raise ClientError("Mixed object types")

    obj_type = objects[0].__class__
    rest_name = obj_type.Meta.rest_name

    url = f"{url}/{rest_name}"
    query_params.setdefault("fields", "all")
    schema = obj_type.Meta.schema(many=True)
    serialized_data = schema.dump(objects)
    json_data = json.dumps({rest_name: serialized_data})
    r = session.put(f"{url}", data=json_data, params=query_params)

    data = r.json()[rest_name]
    if not as_objects:
        return data

    return schema.load(data)


def delete_objects(session: Session, url: str, objects: List[Object]):
    if not objects:
        return

    are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
    if not all(are_same):
        raise ClientError("Mixed object types")

    obj_type = objects[0].__class__
    rest_name = obj_type.Meta.rest_name
    url = f"{url}/{rest_name}"
    data = json.dumps({"source_ids": [obj.id for obj in objects]})

    r = session.delete(url, data=data)