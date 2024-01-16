# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------

from marshmallow import fields

from ansys.hps.client.common import ObjectSchemaWithModificationInfo

from .object_reference import IdReference


class FileSchema(ObjectSchemaWithModificationInfo):
    class Meta(ObjectSchemaWithModificationInfo.Meta):
        pass

    name = fields.String(metadata={"description": "Name of the file resource."})
    type = fields.String(
        allow_none=True,
        metadata={
            "description": "Type of the file. This can be any string but using a correct media "
            "type for the given resource is advisable."
        },
    )
    storage_id = fields.String(
        allow_none=True,
        metadata={"description": "File's identifier in the (orthogonal) file storage system"},
    )

    size = fields.Int(allow_none=True)
    hash = fields.String(allow_none=True)

    expiry_time = fields.DateTime(
        allow_none=True,
        metadata={"description": "File expiration time."},
    )

    format = fields.String(allow_none=True)
    evaluation_path = fields.String(
        allow_none=True,
        metadata={
            "description": "Relative path under which the file instance for a "
            "job evaluation will be stored.",
        },
    )

    monitor = fields.Bool(
        allow_none=True, metadata={"description": "Whether to live monitor the file's content."}
    )
    collect = fields.Bool(
        allow_none=True, metadata={"description": "Whether file should be collected per job"}
    )
    collect_interval = fields.Int(
        allow_none=True,
        metadata={
            "description": "Collect frequency for a file with collect=True."
            " Min value limited by the evaluator's settings."
            " 0/None - let the evaluator decide,"
            " other value - interval in seconds"
        },
    )

    reference_id = IdReference(
        attribute="reference_id",
        referenced_class="File",
        allow_none=True,
        metadata={"description": "Reference file from which this one was created"},
    )
