# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.parameter_mapping import ParameterMappingSchema
from .base import Object, create_objects, delete_objects, get_objects

log = logging.getLogger(__name__)


class ParameterMapping(Object):
    """ParameterMapping resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the ParameterMapping schema below.

    Example:

        >>> pl = ParameterMapping(key_string='radius(0)', tokenizer="=", parameter_definition_name="tube_radius")

    The ParameterMapping schema has the following fields:

    .. jsonschema:: schemas/ParameterMapping.json

    """ 
    class Meta:
        schema = ParameterMappingSchema
        rest_name = "parameter_mappings"

    def __init__(self, **kwargs):
        super(ParameterMapping, self).__init__(**kwargs) 

ParameterMappingSchema.Meta.object_class = ParameterMapping
