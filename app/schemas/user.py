from marshmallow import Schema, fields
from .role import RoleSchema

class UserSchema(Schema):

    id = fields.Integer(dump_only=True)
    email = fields.Email()
    username = fields.String()
    age = fields.Integer()
    gender = fields.String()
    age_of_onset = fields.Integer()
    seizure_type = fields.String()
    caregiver_name = fields.String()
    caregiver_contact = fields.String()
    institution = fields.String()
    profileImage = fields.String()
    password = fields.String(load_only=True)
    roles = fields.Nested(RoleSchema, many=True, dump_only=True)


class UserLoginSchema(Schema):

    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True)
    username = fields.String()
    password = fields.String(load_only=True, required=True)
