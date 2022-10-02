from marshmallow import Schema, fields


class ActivitiesSchema(Schema):

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True, error_message={
        "required": "user_id is required" })
    engaged_socially_today = fields.Boolean()
    engagement_activities = fields.List()
    timestamp = fields.Date(dump_only=True)