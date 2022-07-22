from marshmallow import Schema, fields


class MedicineSchema(Schema):

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True, error_message={
        "required": "user_id is required" })
    name = fields.String(required=True)
