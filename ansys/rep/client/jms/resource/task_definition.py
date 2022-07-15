# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.task_definition import (
    LicensingSchema,
    ResourceRequirementsSchema,
    SoftwareSchema,
    SuccessCriteriaSchema,
    TaskDefinitionSchema,
)
from .base import Object

log = logging.getLogger(__name__)


class Software(Object):
    class Meta:
        schema = SoftwareSchema

    def __init__(self, **kwargs):
        super(Software, self).__init__(**kwargs)


SoftwareSchema.Meta.object_class = Software


class ResourceRequirements(Object):
    class Meta:
        schema = ResourceRequirementsSchema

    def __init__(self, **kwargs):
        super(ResourceRequirements, self).__init__(**kwargs)


ResourceRequirementsSchema.Meta.object_class = ResourceRequirements


class SuccessCriteria(Object):
    """SuccessCriteria resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the SuccessCriteria schema below.

    Example:

        >>> sc = SuccessCriteria(
                return_code=0,
                expressions= ["values['tube1_radius']>=4.0", "values['tube1_thickness']>=0.5"],
                required_output_file_ids=[ f.id for f in files[2:] ],
                require_all_output_files=False,
                required_output_parameter_ids=[...],
                require_all_output_parameters=False
            )

    The SuccessCriteria schema has the following fields:

    .. jsonschema:: schemas/SuccessCriteria.json

    """

    class Meta:
        schema = SuccessCriteriaSchema

    def __init__(self, **kwargs):
        super(SuccessCriteria, self).__init__(**kwargs)


SuccessCriteriaSchema.Meta.object_class = SuccessCriteria


class Licensing(Object):
    """Licensing resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the Licensing schema below.

    Example:

        >>> lic = Licensing(enable_shared_licensing=true)

    The Licensing schema has the following fields:

    .. jsonschema:: schemas/Licensing.json

    """

    class Meta:
        schema = LicensingSchema

    def __init__(self, **kwargs):
        super(Licensing, self).__init__(**kwargs)


LicensingSchema.Meta.object_class = Licensing


class TaskDefinition(Object):
    """TaskDefinition resource.

    Args:
        **kwargs: Arbitrary keyword arguments, see the TaskDefinition schema below.

    Example:

        >>> ps = TaskDefinition(
                    name="MAPDL_run",
                    application_name="ANSYS Mechanical APDL",
                    application_version="20.1",
                    execution_command="%executable% -b -i %file:mac% -o file.out -np %num_cores%",
                    max_execution_time=20.0,
                    cpu_core_usage=1,
                    execution_level=0,
                    memory=250,
                    disk_space=5,
                )

    The TaskDefinition schema has the following fields:

    .. jsonschema:: schemas/TaskDefinition.json

    """

    class Meta:
        schema = TaskDefinitionSchema
        rest_name = "task_definitions"

    def __init__(self, **kwargs):
        super(TaskDefinition, self).__init__(**kwargs)


TaskDefinitionSchema.Meta.object_class = TaskDefinition
