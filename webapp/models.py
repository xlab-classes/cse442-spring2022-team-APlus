from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

db = SQLAlchemy()


class Accounts(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    profile =  db.Column(db.String(200), unique=True, nullable=True)
    Username =  db.Column(db.String(200), unique=True, nullable=True)
    listings = db.relationship('Listings', backref='accounts', cascade="all, delete-orphan")
    liked_posts = db.Column(MutableList.as_mutable(PickleType), default=[])
    saved_posts = db.Column(MutableList.as_mutable(PickleType), default=[])


    def __init__(self, email, password,Username):
        self.email = email
        self.password = password
        self.Username = Username
        db.session.add(self)
        db.session.commit()

    def verify_account(self):
        self.is_verified = True
        db.session.add(self)
        db.session.commit()


class Listings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    title = db.Column(db.String(200), nullable=False)
    likes = db.Column(db.Integer)
    description = db.Column(db.String(1000), nullable=False)
    files = db.relationship('Files', backref='listings', cascade="all, delete-orphan")



class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    file_path = db.Column(db.String(200), unique=True, nullable=False)


class profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    file_path = db.Column(db.String(200), unique=True, nullable=False)


class Msg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    message = db.Column(db.String(2048), nullable=False)

    def __init__(self, sender_id, recipient_id, message):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message = message
        db.session.add(self)
        db.session.commit()
