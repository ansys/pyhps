# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): M.Pawlik, O.Koenig
# ----------------------------------------------------------
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
        super(IdReference, self).__init__(*args, **kwargs)
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
        super(IdReferenceList, self).__init__(*args, **kwargs)
        self.referenced_class = referenced_class

    def _deserialize(self, value, attr, data, **kwargs):
        return id_list_from_ref(value)

    def _serialize(self, value, attr, obj, **kwargs):
        return id_list_to_ref(self.referenced_class, value)

    # def _validate(self, value):
    #     if not isinstance(value, list):
    #         raise ValidationError("Not an object reference list: %s" % value)
