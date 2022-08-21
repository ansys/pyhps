# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.algorithm import AlgorithmSchema
from .base import Object

log = logging.getLogger(__name__)


class Algorithm(Object):
    """Algorithm resource.

    Args:
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

    def __init__(self, **kwargs):
        super(Algorithm, self).__init__(**kwargs)


AlgorithmSchema.Meta.object_class = Algorithm
