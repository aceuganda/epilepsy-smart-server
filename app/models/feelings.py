from sqlalchemy.orm import relationship, backref
from datetime import timedelta
from ..models import db
from app.models.root_model import RootModel
from sqlalchemy.dialects.postgresql import JSON

class Feeling(RootModel):
    """ resilience table definition """

    _tablename_ = "feeling"

    # fields of the user table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    treatment_scale_by_other = db.Column(db.Integer, nullable=False)
    type_of_feelings = db.Column(db.String(256), nullable=False)
    feelings_experienced = db.Column(JSON, nullable=False)
    reason_for_feelings = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())