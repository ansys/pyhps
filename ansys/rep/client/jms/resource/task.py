# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging

from ..schema.task import TaskSchema
from .base import Object

log = logging.getLogger(__name__)


class Task(Object):
    """Task resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the Task schema below.

    The Task schema has the following fields:

    .. jsonschema:: schemas/Task.json

    """

    class Meta:
        schema = TaskSchema
        rest_name = "tasks"

    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)


TaskSchema.Meta.object_class = Task