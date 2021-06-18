from datetime import datetime
from sqlalchemy.sql import expression, func
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, server_default=expression.true(), default=True, nullable=False)
    created = db.Column(db.DateTime, server_default=func.datetime("now"), default=datetime.utcnow, nullable=False)

    username = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(128), unique=True)

    origin = db.Column(db.BigInteger, nullable=True)
    password_hash = db.Column(db.String(256))
    api_key = db.Column(db.String(32), unique=True)

    @property
    def is_active(self):
        return self.active

    def get_id(self):
        return self.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, server_default=expression.true(), default=True, nullable=False)
    anonymous = db.Column(db.Boolean, server_default=expression.true(), default=True, nullable=False)

    origin = db.Column(db.BigInteger, nullable=True)
    expires = db.Column(db.DateTime, nullable=True)

    name = db.Column(db.String(32), unique=True)
    date = db.Column(db.DateTime, server_default=func.datetime("now"), default=datetime.utcnow, nullable=False)
    size = db.Column(db.Integer, nullable=True)

    parent_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent = db.relationship("User", foreign_keys=[parent_id])

class Invite(db.Model):
    __tablename__ = "invites"

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, server_default=expression.true(), default=True, nullable=False)
    created = db.Column(db.DateTime, server_default=func.datetime("now"), default=datetime.utcnow, nullable=False)

    origin = db.Column(db.BigInteger, nullable=True)

    parent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent = db.relationship("User", foreign_keys=[parent_id])

    code = db.Column(db.String(32), unique=True)
    used = db.Column(db.Boolean, nullable=False, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user = db.relationship("User", foreign_keys=[user_id])
