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
"""Module providing the fitness definition and fitness term definition resources."""

import logging

from marshmallow.utils import missing

from ansys.hps.client.common import Object

from ..schema.fitness_definition import FitnessDefinitionSchema, FitnessTermDefinitionSchema

log = logging.getLogger(__name__)


class FitnessTermDefinition(Object):
    """Provides the fitness term definition resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    name : str, optional
        Name of the fitness term.
    expression : str, optional
        Python expression that defines the fitness term.
    type : str, optional
        Fitness term type.
    weighting_factor : float, optional
        Relative importance of the fitness term in comparison to other fitness terms.

    Examples
    --------
    Create a fitness term of the objective type.

    >>> ft1 = FitnessTermDefinition(
    ...     name="weight",
    ...     type="design_objective",
    ...     weighting_factor=1.0,
    ...     expression="map_design_objective(values['weight'],7.5,5.5)"
    ... )

    Create a fitness term of the target constraint type.

    >>> ft2 = FitnessTermDefinition(
    ...     name="torsional_stiffness",
    ...     type="target_constraint",
    ...     weighting_factor=0.8,
    ...     expression="map_target_constraint(
    ...         values['torsion_stiffness'], 1313.0, 5.0, 30.0)"
    ... )

    Create a fitness term of the limit constraint type.

    >>> ft3 = FitnessTermDefinition(
    ...     name="max_stress",
    ...     type="limit_constraint",
    ...     weighting_factor=0.6,
    ...     expression="map_limit_constraint(
    ...         values['max_stress'], 451.0, 50.0 )"
    ... )

    """

    class Meta:
        schema = FitnessTermDefinitionSchema
        rest_name = "None"

    def __init__(
        self,
        id: str = missing,
        name: str = missing,
        expression: str = missing,
        type: str = missing,
        weighting_factor: float = missing,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.expression = expression
        self.type = type
        self.weighting_factor = weighting_factor

        self.obj_type = self.__class__.__name__


FitnessTermDefinitionSchema.Meta.object_class = FitnessTermDefinition


class FitnessDefinition(Object):
    """Provides the fitness definition resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    fitness_term_definitions
        List of :class:`ansys.hps.client.jms.FitnessTermDefinition` objects.
    error_fitness : float
        Default fitness value to assign to failed jobs.

    Examples
    --------
    >>> fd = FitnessDefinition(error_fitness=10.0)
    >>> fd.add_fitness_term(name="weight", type="design_objective", weighting_factor=1.0,
    ...         expression="map_design_objective( values['weight'], 7.5, 5.5)")
    >>> fd.add_fitness_term(name="torsional_stiffness",
    ...                     type="target_constraint",
    ...                     weighting_factor=1.0,
    ...                     expression="map_target_constraint(
    ...                         values['torsion_stiffness'],
    ...                         1313.0,
    ...                         5.0,
    ...                         30.0 )"
    ...                     )

    """

    class Meta:
        schema = FitnessDefinitionSchema
        rest_name = "None"

    def __init__(
        self,
        id: str = missing,
        fitness_term_definitions: list[FitnessTermDefinition] = missing,
        error_fitness: float = missing,
        **kwargs,
    ):
        self.id = id
        self.fitness_term_definitions = fitness_term_definitions
        self.error_fitness = error_fitness

        self.obj_type = self.__class__.__name__

    def add_fitness_term(self, **kwargs):
        """Add a fitness term easily using a helper function."""
        ft = FitnessTermDefinition(**kwargs)

        if self.fitness_term_definitions == missing:
            self.fitness_term_definitions = []
        self.fitness_term_definitions.append(ft)
        return ft


FitnessDefinitionSchema.Meta.object_class = FitnessDefinition
