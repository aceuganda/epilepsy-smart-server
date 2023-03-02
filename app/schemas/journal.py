from marshmallow import Schema, fields


class JournalSchema(Schema):

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True, error_message={
        "required": "user_id is required" })
    title = fields.String()
    notes = fields.String()
    timestamp = fields.Date(dump_only=True)