# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from ansys.rep.client.common import ObjectSchema
from marshmallow import fields
from marshmallow.validate import OneOf

fitness_term_types = ["design_objective", "limit_constraint", "target_constraint"]


class FitnessTermDefinitionSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    name = fields.String(allow_none=True, metadata={"description": "Name of the fitness term."})
    expression = fields.String(
        allow_none=True,
        metadata={"description": "The Python expression that defines the fitness term."},
    )
    type = fields.String(
        allow_none=True,
        validate=OneOf(fitness_term_types),
        metadata={"description": "Fitness term type."},
    )
    weighting_factor = fields.Float(
        allow_none=True,
        metadata={
            "description": "Relative importance of the fitness "
            "term in comparison to other fitness terms."
        },
    )


class FitnessDefinitionSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    fitness_term_definitions = fields.Nested(
        FitnessTermDefinitionSchema,
        many=True,
        metadata={"description": "List of :class:`FitnessTermDefinition`."},
    )
    error_fitness = fields.Float(
        metadata={"description": "The default fitness value assigned to failed jobs."}
    )
