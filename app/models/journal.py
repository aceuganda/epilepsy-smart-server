from app.models import db
from sqlalchemy.orm import relationship, backref
from app.models.root_model import RootModel


class Journal(RootModel):
    _tablename_ = "journals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(256), nullable=True)
    notes = db.Column(db.String(1030), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
