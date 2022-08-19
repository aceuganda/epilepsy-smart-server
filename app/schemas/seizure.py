from marshmallow import Schema, fields


class SeizureSchema(Schema):

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True, error_message={
        "required": "user_id is required" })
    seizure_severity = fields.String()
    seizure_duration = fields.String()
    seizure_time_of_day = fields.String()
    lost_awareness = fields.Boolean()
    experienced_aura = fields.Boolean()
    aura_kind_experienced = fields.String()
    was_seizure_triggered = fields.Boolean()
    seizure_trigger = fields.String()
    seizure_impact = fields.String()
    seizure_impact_upset_you = fields.Integer()
    timestamp = fields.Date(dump_only=True)


