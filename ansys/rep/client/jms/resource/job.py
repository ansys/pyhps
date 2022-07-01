# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import json
import logging

from ..schema.job import JobSchema
from .base import Object, get_objects, update_objects
from .task import Task

log = logging.getLogger(__name__)


class Job(Object):
    """Job resource.

    Args:
        project (:class:`ansys.rep.client.jms.Project`, optional): A Project object. Defaults to None.
        **kwargs: Arbitrary keyword arguments, see the Job schema below.

    Example:

        >>> dps = []
        >>> dps.append( Job( name="dp_1", eval_status="pending") )
        >>> dps.append( Job( name="dp_2", eval_status="pending") )
        >>> project_job_definition.create_jobs( dps )

    The Job schema has the following fields:

    .. jsonschema:: schemas/Job.json

    """

    class Meta:
        schema = JobSchema
        rest_name = "jobs"

    def __init__(self, project=None, **kwargs):
        self.project = project
        super(Job, self).__init__(**kwargs)

    def get_tasks(self, as_objects=True, **query_params):
        """Return a list of tasks, optionally filtered by given query parameters

        Args:
            as_objects (bool, optional): Defaults to True.
            **query_params: Optional query parameters.

        Returns:
            List of :class:`ansys.rep.client.jms.Task` or list of dict if as_objects is False
        """
        return get_objects(
            self.project, Task, job_id=self.id, as_objects=as_objects, **query_params
        )

    def update_tasks(self, tasks, as_objects=True, **query_params):
        """Update existing tasks

        Args:
            tasks (list of :class:`ansys.rep.client.jms.Task`): A list of task objects
            as_objects (bool): Whether to return tasks as objects or dictionaries

        Returns:
            List of :class:`ansys.rep.client.jms.Task` or list of dict if `as_objects` is True
        """
        return update_objects(
            self.project, tasks, job_id=self.id, as_objects=as_objects, **query_params
        )

    def _sync(self):
        sync_jobs(project=self.project, jobs=[self])


JobSchema.Meta.object_class = Job


def copy_jobs(project, jobs, job_definition=None, as_objects=True, **query_params):
    """Create new design points by copying existing ones"""

    url = f"{project.client.jms_api_url}/projects/{project.id}"
    if job_definition:
        url += f"/job_definitions/{job_definition.id}"
    url += f"/jobs"

    query_params.setdefault("fields", "all")

    json_data = json.dumps({"source_ids": [obj.id for obj in jobs]})
    r = project.client.session.post(f"{url}", data=json_data, params=query_params)

    data = r.json()["jobs"]
    if not as_objects:
        return data

    objects = JobSchema(many=True).load(data)
    for o in objects:
        o.project = project
    return objects


def sync_jobs(project, jobs, job_definition=None):

    url = f"{project.client.jms_api_url}/projects/{project.id}"
    if job_definition:
        url += f"/job_definitions/{job_definition.id}"
    url += f"/jobs:sync"

    json_data = json.dumps({"job_ids": [obj.id for obj in jobs]})
    r = project.client.session.put(f"{url}", data=json_data)
