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
"""Module retrieving IDs and providing ID references."""

import logging

from marshmallow import fields

# from ..keys import OBJECT_ID_KEY

log = logging.getLogger(__name__)


def id_from_ref(ref):
    return ref
    # if ref is None:
    #     return None
    # ref_dict = ref.get(OBJECT_REF_KEY)
    # if ref_dict is None:
    #     return None
    # return ref_dict[OBJECT_ID_KEY]


def id_to_ref(cls_name, id):
    return id
    # if id is None:
    #     return None
    # return {OBJECT_REF_KEY : {
    #             OBJECT_TYPE_KEY : cls_name,
    #             OBJECT_ID_KEY : int(id)
    #         }
    #     }


def id_list_to_ref(cls_name, ids):
    return ids
    # return {OBJECT_REF_LIST_KEY : {
    #             OBJECT_TYPE_KEY : cls_name,
    #             OBJECT_ID_LIST_KEY : [int(v) for v in ids]
    #         }
    #     }


def id_list_from_ref(ref):
    return ref
    # if ref is None:
    #     return None
    # ref_dict = ref.get(OBJECT_REF_LIST_KEY)
    # if ref_dict is None:
    #     return None
    # return ref_dict[OBJECT_ID_LIST_KEY]


class IdReference(fields.Field):
    def __init__(self, referenced_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.referenced_class = referenced_class

    def _deserialize(self, value, attr, data, **kwargs):
        return id_from_ref(value)

    def _serialize(self, value, attr, obj, **kwargs):
        return id_to_ref(self.referenced_class, value)

    # def _validate(self, value):
    #     if not isinstance(value, int):
    #         raise ValidationError("Not an object reference: %s" % value)


class IdReferenceList(fields.Field):
    def __init__(self, referenced_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.referenced_class = referenced_class

    def _deserialize(self, value, attr, data, **kwargs):
        return id_list_from_ref(value)

    def _serialize(self, value, attr, obj, **kwargs):
        return id_list_to_ref(self.referenced_class, value)

    # def _validate(self, value):
    #     if not isinstance(value, list):
    #         raise ValidationError("Not an object reference list: %s" % value)
