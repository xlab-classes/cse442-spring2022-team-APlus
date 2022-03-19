from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Accounts(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    #profile =  db.Column(db.String(200), unique=True, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password
        # self.profile = profile 


class Listings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    files = db.relationship('Files', backref='listings')


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    file_path = db.Column(db.String(200), unique=True, nullable=False)

class profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    file_path = db.Column(db.String(200), unique=True, nullable=False)

