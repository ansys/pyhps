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
from ansys.hps.client.common import Object

log = logging.getLogger(__name__)


class FitnessTermDefinition(Object):
    """FitnessTermDefinition resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    name : str, optional 
        Name of the fitness term.
    expression : str, optional
        The Python expression that defines the fitness term.
    type : str, optional
        Fitness term type.
    weighting_factor : float, optional
        Relative importance of the fitness term in comparison to other fitness terms.

    Examples
    --------

    A fitness term of type objective
    
    >>> ft1 = FitnessTermDefinition(
    ...     name="weight",
    ...     type="design_objective",
    ...     weighting_factor=1.0,
    ...     expression="map_design_objective(values['weight'],7.5,5.5)"
    ... )
    
    A fitness term of type target constraint
    
    >>> ft2 = FitnessTermDefinition(
    ...     name="torsional_stiffness",
    ...     type="target_constraint",
    ...     weighting_factor=0.8,
    ...     expression="map_target_constraint(
    ...         values['torsion_stiffness'], 1313.0, 5.0, 30.0)"
    ... )
    
    A fitness term of type limit constraint
    
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

    def __init__(self, **kwargs):
        self.id = missing
        self.name = missing
        self.expression = missing
        self.type = missing
        self.weighting_factor = missing

        super().__init__(**kwargs)


FitnessTermDefinitionSchema.Meta.object_class = FitnessTermDefinition


class FitnessDefinition(Object):
    """FitnessDefinition resource.

    Parameters
    ----------
    id : str, optional
        Unique ID to access the resource, generated internally by the server on creation.
    fitness_term_definitions
        List of :class:`ansys.hps.client.jms.FitnessTermDefinition`.
    error_fitness : float
        The default fitness value assigned to failed design points.

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

    def __init__(self, **kwargs):
        self.id = missing
        self.fitness_term_definitions = missing
        self.error_fitness = missing

        super().__init__(**kwargs)

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
