from marshmallow import Schema, fields


class GratefulSchema(Schema):

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True, error_message={
        "required": "user_id is required" })
    grateful = fields.String()
    timestamp = fields.Date(dump_only=True)
