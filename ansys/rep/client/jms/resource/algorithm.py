# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.algorithm import AlgorithmSchema
from .base import Object, get_objects
from .job import Job
from .selection import get_selections

log = logging.getLogger(__name__)


class Algorithm(Object):
    """Algorithm resource.

    Args:
        project (:class:`ansys.rep.client.jms.Project`, optional): A Project object. Defaults to None.
        **kwargs: Arbitrary keyword arguments, see the Algorithm schema below.

    Example:

        >>> algo = Algorithm(name="gradient_descent")
        >>> algo.description = "Gradient descent is an iterative optimization algorithm."
        >>> algo.data = "{\"step_size\": 0.2,\"max_iterations\":10}"

    The Algorithm schema has the following fields:

    .. jsonschema:: schemas/Algorithm.json

    """

    class Meta:
        schema = AlgorithmSchema
        rest_name = "algorithms"

    def __init__(self, project=None, **kwargs):
        self.project = project
        super(Algorithm, self).__init__(**kwargs)

    def get_jobs(self, as_objects=True, **query_params):
        """Return a list of design points, optionally filtered by given query parameters

        Returns:
            List of :class:`ansys.rep.client.jms.Job` or list of dict if as_objects is False
        """
        return get_objects(
            self.project, Job, as_objects=as_objects, algorithm_id=self.id, **query_params
        )

    def get_selections(self, as_objects=True, **query_params):
        """Return a list of selections, optionally filtered by given query parameters

        Returns:
            List of :class:`ansys.rep.client.jms.Selection` or list of dict if as_objects is False
        """
        return get_selections(
            self.project, as_objects=as_objects, algorithm_id=self.id, **query_params
        )


AlgorithmSchema.Meta.object_class = Algorithm
