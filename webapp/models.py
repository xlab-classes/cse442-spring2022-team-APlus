from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # profile = db.Column(db.Text, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password
        # self.profile = profile 


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile = db.Column(db.String(1000), nullable=False)

    def __init__(self, email, profile):
        self.email = email
        self.profile = profile 
