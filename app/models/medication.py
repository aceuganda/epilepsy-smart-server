from sqlalchemy.orm import relationship, backref
from datetime import timedelta
from ..models import db
from app.models.root_model import RootModel

class Medication(RootModel):
    """ medicine table definition """

    _tablename_ = "medication"
     # fields of the medicine table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    medicine_id = db.Column(db.ForeignKey('medicine.id'), nullable=True)
    took_medicine = db.Column(db.String(256), nullable=False)
    medicine_name = db.Column(db.String(256), nullable=True)
    experienced_side_effects = db.Column(db.Boolean, nullable=True)
    side_effects_experienced = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())


