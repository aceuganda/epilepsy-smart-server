from marshmallow import Schema, fields


class ResilienceSchema(Schema):

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True, error_message={
        "required": "user_id is required" })
    treatment_scale_by_other = fields.Integer()
    engaged_socially_today = fields.Boolean()
    engagement_activities = fields.List(fields.String)
    type_of_feelings = fields.String()
    feelings_experienced = fields.List(fields.String)
    reason_for_feelings = fields.String()
    timestamp = fields.Date(dump_only=True)


