# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.selection import JobSelectionSchema
from .base import Object

log = logging.getLogger(__name__)


class JobSelection(Object):
    """JobSelection resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the Selection schema below.

    Example:

        >>> sel = JobSelection(name="selection_0", jobs=[1,2,15,28,45])

    The JobSelection schema has the following fields:

    .. jsonschema:: schemas/JobSelection.json

    """

    class Meta:
        schema = JobSelectionSchema
        rest_name = "job_selections"

    def __init__(self, **kwargs):
        super(JobSelection, self).__init__(**kwargs)


JobSelectionSchema.Meta.object_class = JobSelection
