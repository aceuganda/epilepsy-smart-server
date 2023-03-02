from sqlalchemy.orm import relationship, backref
from datetime import timedelta
from ..models import db
from app.models.root_model import RootModel

class Grateful(RootModel):
    """ medicine table definition """

    _tablename_ = "medicine"
     # fields of the medicine table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    grateful = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())