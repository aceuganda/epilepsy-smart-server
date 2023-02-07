from flask_bcrypt import Bcrypt
from sqlalchemy.orm import relationship, backref
from datetime import timedelta
from flask_jwt_extended import create_access_token
from ..models import db
from app.models.root_model import RootModel

from app.models.seizure import Seizure
from app.models.medicine import Medicine
class User(RootModel):
    """ user table definition """

    _tablename_ = "users"

    # fields of the user table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True)
    username = db.Column(db.String(256), nullable=False, default="")
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(256), nullable=True)
    age_of_onset = db.Column(db.Integer, nullable=True)
    seizure_type = db.Column(db.String(256), nullable=True)
    caregiver_name = db.Column(db.String(256), nullable=True)
    caregiver_contact = db.Column(db.String(256), nullable=True)
    institution = db.Column(db.String(256), nullable=True)
    profileImage = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(256), nullable=False, default="")
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    seizures = db.relationship('Seizure', backref='user', lazy=True)
    medicines =db.relationship('Medicine', backref='user', lazy=True)

    def __init__(self, username, email, age, gender, age_of_onset, seizure_type, caregiver_name, caregiver_contact, institution, profileImage, password):
        """ initialize with email, age, gender, age_of_onset, seizure_type, caregiver_name, caregiver_contact, institution, profileImage, username and password """
        self.email = email
        self.username = username
        self.age = age
        self.gender= gender
        self.age_of_onset = age_of_onset
        self.seizure_type = seizure_type
        self.caregiver_name = caregiver_name
        self.caregiver_contact = caregiver_contact
        self.institution = institution
        self.profileImage = profileImage
        self.password = Bcrypt().generate_password_hash(password).decode()

    # to be used on login
    def password_is_valid(self, password):
        """ checks the password against it's hash to validate the user's password """
        return Bcrypt().check_password_hash(self.password, password)

    # to be used to generate user token
    def generate_token(self, user):
        """ generates the access token """
        # set token expiry period
        expiry = timedelta(days=100)
        roles = user["roles"]

        return create_access_token(user, expires_delta=expiry, user_claims=dict({"roles":roles}))

    def __repr__(self):
        return "<User: {}>".format(self.email)
