# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import json
import logging

from marshmallow.utils import missing

log = logging.getLogger(__name__)


class Object(object):
    class Meta:
        schema = None  # To be set in derived classes
        rest_name = (
            None  # String used in REST URI's to access this resource, to be set in derived classes
        )

    def declared_fields(self):
        """
        Helper function to retrieve the fields that will be defined as class members for an object
        """
        fields = []
        for k, v in self.Meta.schema._declared_fields.items():
            field = k
            # Ensure that we use the attribute name if defined
            if getattr(v, "attribute", None) is not None:
                field = v.attribute
            fields.append(field)
        return fields

    def __init__(self, **kwargs):
        # obj_type in JSON equals class name in API
        self.obj_type = self.__class__.__name__

        # Instantiate class members for all fields of the corresponding schema
        for k in self.declared_fields():

            # If property k is provided as init parameter
            if k in kwargs.keys():
                setattr(self, k, kwargs[k])
            # Else we set it this value as missing.
            # That way marshmallow will ignore it on serialization
            elif not hasattr(self, k):
                setattr(self, k, missing)

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ",".join(["%s=%r" % (k, getattr(self, k)) for k in self.declared_fields()]),
        )

    def __str__(self):
        return json.dumps(self.Meta.schema(many=False).dump(self), indent=2)
