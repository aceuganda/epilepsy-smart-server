from sqlalchemy.orm import relationship, backref
from datetime import timedelta
from ..models import db
from app.models.root_model import RootModel


class Seizure(RootModel):
    """ user table definition """

    _tablename_ = "seizure"

    # fields of the user table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seizure_severity = db.Column(db.String(256), nullable=False)
    seizure_duration = db.Column(db.String(256), nullable=False)
    seizure_time_of_day = db.Column(db.String(256), nullable=False)
    lost_awareness = db.Column(db.Boolean(256), nullable=False)
    experienced_aura = db.Column(db.Boolean, nullable=False)
    aura_kind_experienced = db.Column(db.String(256), nullable=True)
    was_seizure_triggered = db.Column(db.Boolean, nullable=False)
    seizure_trigger = db.Column(db.String(256),nullable=True)
    seizure_impact = db.Column(db.String(256), nullable=False)
    seizure_impact_upset_you = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

