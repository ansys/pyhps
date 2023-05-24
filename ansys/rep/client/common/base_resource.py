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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # log.info(f"**eq check for {self.__class__}")
            for k in self.declared_fields():
                # log.info(f"***check on {k}")
                # log.info(f"***self.{k} = {getattr(self, k, None)}")
                # log.info(f"***other.{k} = {getattr(other, k, None)}")
                if not hasattr(other, k) or getattr(self, k, None) != getattr(other, k, None):
                    # log.warning(f"*** Negative check")
                    return False
            return True
        # log.warning(f"**Not an instance of {self.__class__}")
        return NotImplemented

    def __str__(self):

        # Ideally we'd simply do
        #   return json.dumps(self.Meta.schema(many=False).dump(self), indent=2)
        # However the schema.dump() function (rightfully) ignores fields marked as load_only.
        #
        # Therefore we have to manually iterate over all fields

        schema = self.Meta.schema(many=False)
        dict_repr = schema.dict_class()
        for attr_name, field_obj in schema.fields.items():
            value = missing
            try:
                value = field_obj.serialize(attr_name, self, accessor=schema.get_attribute)
            except:
                pass
            if value is missing:
                continue
            key = field_obj.data_key if field_obj.data_key is not None else attr_name
            dict_repr[key] = value

        return json.dumps(dict_repr, indent=2)
