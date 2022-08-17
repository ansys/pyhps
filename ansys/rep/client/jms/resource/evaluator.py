# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
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
        schema = EvaluatorSchema
        rest_name = "evaluators"

    def __init__(self, **kwargs):
        super(Evaluator, self).__init__(**kwargs)


EvaluatorSchema.Meta.object_class = Evaluator
