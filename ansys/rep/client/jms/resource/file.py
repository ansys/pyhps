# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ..schema.file import FileSchema
from .base import Object

log = logging.getLogger(__name__)


class File(Object):
    """File resource.

    Args:
        src (str, optional): Path to the local file. Defaults to None.
        **kwargs: Arbitrary keyword arguments, see the File schema below.

    Example:

        >>> # input file
        >>> f1 = File(name="mac", evaluation_path="demo_project.mac",
                        type="text/plain", src=os.path.join(os.getcwd(), "motorbike_frame.mac")
        >>> # output file
        >>> f2 = File(name="img", evaluation_path="file000.jpg", type="image/jpeg") )

    The File schema has the following fields:

    .. jsonschema:: schemas/File.json

    """

    class Meta:
        schema = FileSchema
        rest_name = "files"

    def __init__(self, src=None, **kwargs):
        self.src = src
        self.content = None
        super(File, self).__init__(**kwargs)


FileSchema.Meta.object_class = File
