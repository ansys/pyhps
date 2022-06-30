# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import json

from marshmallow.utils import missing

from ..schema.evaluator import EvaluatorSchema
from .base import Object

class Evaluator(Object):
    """Evaluator resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the Evaluator schema below.
        
    The Evaluator schema has the following fields:

    .. jsonschema:: schemas/Evaluator.json

    """
    class Meta:
        schema=EvaluatorSchema
        rest_name = "evaluators"

    def __init__(self, **kwargs):
        super(Evaluator, self).__init__(**kwargs)

    # def __init__(self, project=None, **kwargs):
    #     self.project=project
    #     super(Evaluator, self).__init__(**kwargs)

EvaluatorSchema.Meta.object_class = Evaluator

def get_evaluators(client, as_objects=True, **query_params):
    """
    Returns list of evaluators
    """
    url = f"{client.jms_api_url}/evaluators"
    query_params.setdefault("fields", "all")
    r = client.session.get(url, params=query_params)
    
    data = r.json()['evaluators'] 
    if not as_objects:
        return data

    evaluators  = EvaluatorSchema(many=True).load( data )
    return evaluators

def update_evaluators(client, evaluators, as_objects=True, **query_params):
    """
    Update evaluator job_definition
    """
    url = f"{client.jms_api_url}/evaluators"
    
    schema =  EvaluatorSchema(many=True)
    serialized_data = schema.dump(evaluators)
    json_data = json.dumps({"evaluators": [serialized_data]})
    query_params.setdefault("fields", "all")
    r = client.session.put(f"{url}", data=json_data, params=query_params)

    data =  r.json()['evaluators'][0]
    if not as_objects:
        return data

    objects=schema.load( data )
    return objects