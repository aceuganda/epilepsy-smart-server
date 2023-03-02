from app.models import db
from sqlalchemy.orm import relationship, backref
from app.models.user import User
from app.models.root_model import RootModel


class Journal(RootModel):
    _tablename_ = "journal"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey(User.id))
    title = db.Column(db.String(256), nullable=True)
    notes = db.Column(db.String(1030), nullable=True)
