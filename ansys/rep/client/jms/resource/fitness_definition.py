# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from marshmallow.utils import missing

from ..schema.fitness_definition import FitnessDefinitionSchema, FitnessTermDefinitionSchema
from .base import Object

log = logging.getLogger(__name__)


class FitnessTermDefinition(Object):
    """FitnessTermDefinition resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the FitnessTermDefinition schema below.

    The FitnessTermDefinition schema has the following fields:

    .. jsonschema:: schemas/FitnessTermDefinition.json

    Example:

        >>> # A fitness term of type objective
        >>> ft1 = FitnessTermDefinition(name="weight",
                                        type="design_objective",
                                        weighting_factor=1.0,
                                        expression="map_design_objective(values['weight'],7.5,5.5)"
                                        )
        >>> # A fitness term of type target constraint
        >>> ft2 = FitnessTermDefinition(name="torsional_stiffness",
                                        type="target_constraint",
                                        weighting_factor=0.8,
                                        expression="map_target_constraint(
                                            values['torsion_stiffness'], 1313.0, 5.0, 30.0)"
                                        )
        >>> # A fitness term of type limit constraint
        >>> ft3 = FitnessTermDefinition(name="max_stress",
                                        type="limit_constraint",
                                        weighting_factor=0.6,
                                        expression="map_limit_constraint(
                                            values['max_stress'], 451.0, 50.0 )"
                                        )
    """

    class Meta:
        schema = FitnessTermDefinitionSchema

    def __init__(self, **kwargs):
        super(FitnessTermDefinition, self).__init__(**kwargs)


FitnessTermDefinitionSchema.Meta.object_class = FitnessTermDefinition


class FitnessDefinition(Object):
    """FitnessDefinition resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the Job schema below.

    Example:

        >>> fd = FitnessDefinition(error_fitness=10.0)
        >>> fd.add_fitness_term(name="weight", type="design_objective", weighting_factor=1.0,
                    expression="map_design_objective( values['weight'], 7.5, 5.5)")
        >>> fd.add_fitness_term(name="torsional_stiffness",
                                type="target_constraint",
                                weighting_factor=1.0,
                                expression="map_target_constraint(
                                    values['torsion_stiffness'],
                                    1313.0,
                                    5.0,
                                    30.0 )" )

    The FitnessDefinition schema has the following fields:

    .. jsonschema:: schemas/FitnessDefinition.json

    """

    class Meta:
        schema = FitnessDefinitionSchema

    def __init__(self, **kwargs):
        super(FitnessDefinition, self).__init__(**kwargs)

    def add_fitness_term(self, **kwargs):
        """
        Helper function to easily add a fitness term
        """
        ft = FitnessTermDefinition(**kwargs)

        if self.fitness_term_definitions == missing:
            self.fitness_term_definitions = []
        self.fitness_term_definitions.append(ft)
        return ft


FitnessDefinitionSchema.Meta.object_class = FitnessDefinition
