from sqlalchemy.orm import relationship, backref
from datetime import timedelta
from ..models import db
from app.models.root_model import RootModel

class Medicine(RootModel):
    """ medicine table definition """

    _tablename_ = "medicine"
     # fields of the medicine table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False, default="")
    medications =db.relationship('Medication', backref='medicine', lazy=True)
