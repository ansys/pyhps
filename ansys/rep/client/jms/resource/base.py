# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
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
        # return "%s(%s)" % (self.__class__.__name__,
        # ",".join(["%s=%r" %(k,v) for k,v in self.__dict__.items()]) )

    def __str__(self):
        return "%s(\n%s\n)" % (
            self.__class__.__name__,
            ",\n".join(["%s=%r" % (k, getattr(self, k)) for k in self.declared_fields()]),
        )
        # return "{%s\n}" % ("\n".join(["%s: %s" %(k,str(v)) for k,v in self.__dict__.items()]) )


# def get_objects(project, obj_type, job_definition=None, as_objects=True, **query_params):
#     """Reusable function to get objects in a project"""
#     rest_name = obj_type.Meta.rest_name
#     url = f"{project.client.jms_api_url}/projects/{project.id}"
#     if job_definition is not None:
#         url += f"/job_definitions/{job_definition.id}"
#     url += f"/{rest_name}"

#     query_params.setdefault("fields", "all")

#     r = project.client.session.get(url, params=query_params)

#     if query_params.get("count"):
#         return r.json()[f"num_{rest_name}"]

#     data = r.json()[rest_name]
#     if not as_objects:
#         return data

#     schema = obj_type.Meta.schema(many=True)
#     objects = schema.load(data)
#     for o in objects:
#         o.project = project
#     return objects


# def create_objects(project, objects, as_objects=True, **query_params):

#     if not objects:
#         return []

#     are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
#     if not all(are_same):
#         raise REPError("Mixed object types")

#     obj_type = objects[0].__class__
#     rest_name = obj_type.Meta.rest_name
#     url = f"{project.client.jms_api_url}/projects/{project.id}/{rest_name}"

#     query_params.setdefault("fields", "all")

#     schema = obj_type.Meta.schema(many=True)
#     serialized_data = schema.dump(objects)
#     json_data = json.dumps({rest_name: serialized_data})
#     r = project.client.session.post(f"{url}", data=json_data, params=query_params)

#     data = r.json()[rest_name]
#     if not as_objects:
#         return data

#     objects = schema.load(data)
#     for o in objects:
#         o.project = project
#     return objects


# def update_objects(project, objects, as_objects=True, **query_params):

#     if not objects:
#         return []

#     are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
#     if not all(are_same):
#         raise REPError("Mixed object types")

#     obj_type = objects[0].__class__
#     rest_name = obj_type.Meta.rest_name
#     url = f"{project.client.jms_api_url}/projects/{project.id}/{rest_name}"

#     query_params.setdefault("fields", "all")

#     schema = obj_type.Meta.schema(many=True)
#     serialized_data = schema.dump(objects)
#     json_data = json.dumps({rest_name: serialized_data})
#     r = project.client.session.put(f"{url}", data=json_data, params=query_params)

#     data = r.json()[rest_name]
#     if not as_objects:
#         return data

#     objects = schema.load(data)
#     for o in objects:
#         o.project = project
#     return objects


# def delete_objects(project, objects):
#     """Reusable delete function"""

#     if not objects:
#         return

#     are_same = [o.__class__ == objects[0].__class__ for o in objects[1:]]
#     if not all(are_same):
#         raise REPError("Mixed object types")

#     obj_type = objects[0].__class__
#     rest_name = obj_type.Meta.rest_name
#     url = f"{project.client.jms_api_url}/projects/{project.id}/{rest_name}"

#     data = json.dumps({"source_ids": [obj.id for obj in objects]})
#     r = project.client.session.delete(url, data=data)
