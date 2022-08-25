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
from .base import Object

log = logging.getLogger(__name__)


class Job(Object):
    """Job resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the Job schema below.

    Example:

        >>> jobs = []
        >>> jobs.append( Job( name="job_1", eval_status="pending", job_definition_id=job_def.id) )
        >>> jobs.append( Job( name="job_2", eval_status="pending", job_definition_id=job_def.id) )
        >>> project_api.create_jobs( jobs )

    The Job schema has the following fields:

    .. jsonschema:: schemas/Job.json

    """

    class Meta:
        schema = JobSchema
        rest_name = "jobs"

    def __init__(self, **kwargs):
        super(Job, self).__init__(**kwargs)


JobSchema.Meta.object_class = Job


def copy_jobs(project_api, jobs, as_objects=True, **query_params):
    """Create new jobs by copying existing ones"""

    url = f"{project_api.url}/jobs"

    query_params.setdefault("fields", "all")

    json_data = json.dumps({"source_ids": [obj.id for obj in jobs]})
    r = project_api.client.session.post(f"{url}", data=json_data, params=query_params)

    data = r.json()["jobs"]
    if not as_objects:
        return data

    return JobSchema(many=True).load(data)


def sync_jobs(project_api, jobs):

    url = f"{project_api.url}/jobs:sync"
    json_data = json.dumps({"job_ids": [obj.id for obj in jobs]})
    r = project_api.client.session.put(f"{url}", data=json_data)
