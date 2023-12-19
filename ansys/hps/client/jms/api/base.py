import json
import logging
from typing import List, Type

from requests import Session

from ansys.hps.client.common import Object
from ansys.hps.client.exceptions import ClientError

log = logging.getLogger(__name__)


def get_objects(
    session: Session, url: str, obj_type: Type[Object], as_objects=True, **query_params
):

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
    session: Session, url: str, obj_type: Type[Object], id: str, as_object=True, **query_params
):

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
    objects: List[Object],
    obj_type: Type[Object],
    as_objects=True,
    **query_params,
):

    if objects is None:
        raise ClientError("objects can't be None")

    are_same = [o.__class__ == obj_type for o in objects]
    if not all(are_same):
        raise ClientError("Mixed object types")

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


def copy_objects(session: Session, url: str, objects: List[Object], wait: bool = True) -> str:

    are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
    if not all(are_same):
        raise ClientError("Mixed object types")

    obj_type = objects[0].__class__
    rest_name = obj_type.Meta.rest_name
    url = f"{url}/{rest_name}:copy"  # noqa: E231

    source_ids = [obj.id for obj in objects]
    r = session.post(url, data=json.dumps({"source_ids": source_ids}))

    operation_location = r.headers["location"]
    operation_id = operation_location.rsplit("/", 1)[-1]

    return operation_id
