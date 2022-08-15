# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.license_context import LicenseContextSchema
from .base import Object

log = logging.getLogger(__name__)


class LicenseContext(Object):
    """
    License context resource

    Example:

        >>> lc = LicenseContext(
            environment={"ANSYS_HPC_PARAMETRIC_ID": "my_id",
                         "ANSYS_HPC_PARAMETRIC_SERVER":"my_server" }
            )
            )

    The LicenseContext schema has the following fields:

    .. jsonschema:: schemas/LicenseContext.json

    """

    class Meta:
        schema = LicenseContextSchema
        rest_name = "license_contexts"

    def __init__(self, **kwargs):
        super(LicenseContext, self).__init__(**kwargs)


LicenseContextSchema.Meta.object_class = LicenseContext
