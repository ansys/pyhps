# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.selection import SelectionSchema
from .base import Object

log = logging.getLogger(__name__)


class Selection(Object):
    """Selection resource.

    Args:
        project (:class:`ansys.rep.client.jms.Project`, optional): Project object. Defaults to None.
        **kwargs: Arbitrary keyword arguments, see the Selection schema below.

    Example:

        >>> sel = Selection(name="selection_0", jobs=[1,2,15,28,45])

    The Selection schema has the following fields:

    .. jsonschema:: schemas/Selection.json

    """

    class Meta:
        schema = SelectionSchema

    def __init__(self, **kwargs):
        super(Selection, self).__init__(**kwargs)


SelectionSchema.Meta.object_class = Selection
