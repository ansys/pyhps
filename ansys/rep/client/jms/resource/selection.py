# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import json
import logging

from ..schema.selection import SelectionSchema
from .base import Object, get_objects
from .job_definition import Job

log = logging.getLogger(__name__)


class Selection(Object):
    """Selection resource.

    Args:
        project (:class:`ansys.rep.client.jms.Project`, optional): A Project object. Defaults to None.
        **kwargs: Arbitrary keyword arguments, see the Selection schema below.

    Example:

        >>> sel = Selection(name="selection_0", jobs=[1,2,15,28,45])

    The Selection schema has the following fields:

    .. jsonschema:: schemas/Selection.json

    """

    class Meta:
        schema = SelectionSchema

    def __init__(self, project=None, **kwargs):
        self.project = project
        super(Selection, self).__init__(**kwargs)

    def get_jobs(self, as_objects=True, **query_params):
        """Return a list of design points, optionally filtered by given query parameters

        Returns:
            List of :class:`ansys.rep.client.jms.Job` or list of dict if as_objects is True
        """
        return get_objects(
            self.project, Job, as_objects=as_objects, selection=self.name, **query_params
        )


SelectionSchema.Meta.object_class = Selection


def get_selections(project, job_definition=None, as_objects=True, **query_params):
    url = f"{project.client.jms_api_url}/projects/{project.id}"
    if job_definition:
        url += f"/job_definitions/{job_definition.id}"
    url += f"/jobs/selections"

    query_params.setdefault("fields", "all")
    r = project.client.session.get(url, params=query_params)

    if query_params.get("count"):
        return r.json()["num_selections"]

    data = r.json()["selections"]
    if not as_objects:
        return data

    schema = SelectionSchema(many=True)
    objects = schema.load(data)
    for o in objects:
        o.project = project
    return objects


def create_selections(project, objects, as_objects=True, **query_params):
    url = f"{project.client.jms_api_url}/projects/{project.id}/jobs/selections"

    schema = SelectionSchema(many=True)
    serialized_data = schema.dump(objects)
    json_data = json.dumps({"selections": serialized_data})
    query_params.setdefault("fields", "all")
    r = project.client.session.post(f"{url}", data=json_data, params=query_params)

    data = r.json()["selections"]
    if not as_objects:
        return data

    objects = schema.load(data)
    for o in objects:
        o.project = project
    return objects


def update_selections(project, objects, as_objects=True, **query_params):
    url = f"{project.client.jms_api_url}/projects/{project.id}/jobs/selections"

    schema = SelectionSchema(many=True)
    serialized_data = schema.dump(objects)
    json_data = json.dumps({"selections": serialized_data})
    query_params.setdefault("fields", "all")
    r = project.client.session.put(f"{url}", data=json_data, params=query_params)

    data = r.json()["selections"]
    if not as_objects:
        return data

    objects = schema.load(data)
    for o in objects:
        o.project = project
    return objects


def delete_selections(project, objects):
    url = f"{project.client.jms_api_url}/projects/{project.id}/jobs/selections"

    data = json.dumps({"source_ids": [obj.id for obj in objects]})
    r = project.client.session.delete(url, data=data)
