from marshmallow import Schema, fields


class MedicationSchema(Schema):

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True, error_message={
        "required": "user_id is required" })
    medicine_id = fields.Integer(required=True, error_message={
    "required": "medicine_id is required" })
    took_medicine = fields.String(required=True)
    reason_missed_dose = fields.String()
    medicine_name = fields.String()
    experienced_side_effects = fields.Boolean(required=True)
    side_effects_experienced = fields.String()
    timestamp = fields.Date(dump_only=True)
