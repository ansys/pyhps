from marshmallow import fields
from marshmallow.exceptions import ValidationError


class AnyValue(fields.Field):
    any_fields = [
        fields.Int(strict=True),
        fields.Bool(truthy=[True], falsy=[False]),
        fields.Str(),
        fields.Float(allow_nan=False),
    ]

    def __init__(self):
        super().__init__(allow_none=True)

    def _deserialize(self, value, attr, obj, **kwargs):
        for field in self.any_fields:
            try:
                return field._deserialize(value, attr, obj, **kwargs)
            except:
                pass

        self.raise_validation_error()

    def raise_validation_error():
        raise ValidationError("Value must be of type float, integer, boolean, or string")
