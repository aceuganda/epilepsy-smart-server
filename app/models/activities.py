from sqlalchemy.orm import relationship, backref
from datetime import timedelta
from ..models import db
from app.models.root_model import RootModel
from sqlalchemy.dialects.postgresql import JSON

class Activity(RootModel):
    """ activity table definition """

    _tablename_ = "activity"

    # fields of the user table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    engaged_socially_today = db.Column(db.Boolean(256), nullable=False)
    engagement_activities = db.Column(JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())