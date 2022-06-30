# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from marshmallow.utils import missing

from ..schema.job_definition import JobDefinitionSchema
from .base import Object, create_objects, delete_objects, get_objects
from .job import Job, copy_jobs
from .parameter_definition import (BoolParameterDefinition,
                                   FloatParameterDefinition,
                                   IntParameterDefinition,
                                   StringParameterDefinition)
from .parameter_mapping import ParameterMapping
from .task_definition import TaskDefinition

log = logging.getLogger(__name__)

class JobDefinition(Object):
    """JobDefinition resource.

    Args:
        project (:class:`ansys.rep.client.jms.Project`, optional): A Project object. Defaults to None.
        **kwargs: Arbitrary keyword arguments, see the JobDefinition schema below.

    Example:

        >>> job_def = JobDefinition(name="JobDefinition.1", active=True)
        >>> job_def.add_float_parameter_definition(name='tube_radius', lower_limit=4.0, upper_limit=20.0,default=12.0 )

    The JobDefinition schema has the following fields:

    .. jsonschema:: schemas/JobDefinition.json

    """
    class Meta:
        schema=JobDefinitionSchema
        rest_name = "job_definitions"

    def __init__(self, project=None, **kwargs):
        self.project=project
        super(JobDefinition, self).__init__(**kwargs)

    def get_jobs(self, **query_params):
        """Return a list of desing points, optionally filtered by given query parameters """
        return get_objects(self.project, Job, job_definition=self, **query_params)

    def create_jobs(self, jobs):
        for j in jobs: j.job_definition_id = self.id
        return create_objects(self.project, jobs)

    def copy_jobs(self, jobs):
        return copy_jobs(self.project, jobs, job_definition=self)

    def delete_jobs(self, jobs):
        return delete_objects(self.project, jobs)

JobDefinitionSchema.Meta.object_class = JobDefinition
