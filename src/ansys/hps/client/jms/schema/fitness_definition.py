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
"""Module providing fitness term definition schema."""

from marshmallow import fields
from marshmallow.validate import OneOf

from ansys.hps.client.common import ObjectSchema

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
