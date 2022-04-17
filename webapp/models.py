from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Accounts(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    listings = db.relationship('Listings', backref='accounts', cascade="all, delete-orphan")

    def __init__(self, email, password):
        self.email = email
        self.password = password
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

# class EditListings(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
#     title = db.Column(db.String(200), nullable=False)
#     description = db.Column(db.String(1000), nullable=False)
#     files = db.relationship('Files', backref='listings', cascade="all, delete-orphan")