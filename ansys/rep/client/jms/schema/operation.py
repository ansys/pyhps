from marshmallow import fields

from .base import ObjectSchema


class OperationSchema(ObjectSchema):
    class Meta(ObjectSchema.Meta):
        pass

    name = fields.String(allow_none=True)
    finished = fields.Bool(allow_none=True)
    succeeded = fields.Bool(allow_none=True)

    progress = fields.Float(allow_none=True)
    status = fields.String(allow_none=True)
    result = fields.Dict(allow_none=True)
    messages = fields.List(fields.Dict(), allow_none=True)

    start_time = fields.DateTime(allow_none=True)
    end_time = fields.DateTime(allow_none=True)
