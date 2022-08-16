# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.job_definition import JobDefinitionSchema
from .base import Object

log = logging.getLogger(__name__)


class JobDefinition(Object):
    """JobDefinition resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the JobDefinition schema below.

    Example:

        >>> job_def = JobDefinition(name="JobDefinition.1", active=True)
        >>> job_def.add_float_parameter_definition(name='tube_radius',
                                                   lower_limit=4.0,
                                                   upper_limit=20.0,
                                                   default=12.0 )

    The JobDefinition schema has the following fields:

    .. jsonschema:: schemas/JobDefinition.json

    """

    class Meta:
        schema = JobDefinitionSchema
        rest_name = "job_definitions"

    def __init__(self, **kwargs):
        super(JobDefinition, self).__init__(**kwargs)


JobDefinitionSchema.Meta.object_class = JobDefinition
