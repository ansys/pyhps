# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module processing class members for an object."""

import json
import logging

from marshmallow.utils import missing

log = logging.getLogger(__name__)


class Object:
    """Base resource object."""

    class Meta:
        """Meta class for the object."""

        schema = None  # To be set in derived classes
        rest_name = (
            None  # String used in REST URI's to access this resource, to be set in derived classes
        )

    def declared_fields(self):
        """Provide a helper function for retrieving fields."""
        fields = []
        for k, v in self.Meta.schema._declared_fields.items():
            field = k
            # Ensure that we use the attribute name if defined
            if getattr(v, "attribute", None) is not None:
                field = v.attribute
            fields.append(field)
        return fields

    def __init__(self, **kwargs):
        """Initialize the object."""
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
        """Printable representation of the object."""
        return "%s(%s)" % (  # noqa
            self.__class__.__name__,
            ",".join(["%s=%r" % (k, getattr(self, k)) for k in self.declared_fields()]),  # noqa
        )

    def __eq__(self, other):
        """Compare instances of the object."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        for k in self.declared_fields():
            if not hasattr(other, k) or getattr(self, k, None) != getattr(other, k, None):
                return False
        return True

    def __str__(self):
        """Provide the string representation of the object."""
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
            except Exception:
                pass
            if value is missing:
                continue
            key = field_obj.data_key if field_obj.data_key is not None else attr_name
            dict_repr[key] = value

        return json.dumps(dict_repr, indent=2)

    def __getitem__(self, key):
        """Get item from object."""
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Set item in object."""
        return setattr(self, key, value)

    def get(self, key, default=None):
        """Get an item from the object, returning a default value if the key is not found."""
        return getattr(self, key, default)
