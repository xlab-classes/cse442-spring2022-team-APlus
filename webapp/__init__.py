from flask import Flask
from webapp.models import db
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

sql_database = 'mysql+pymysql://{0}:{1}@oceanus.cse.buffalo.edu/{0}_db'.format('jchi3','50266661')
app.config['SECRET-KEY'] = 'mySecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = sql_database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db.init_app(app)
with app.app_context():
    # Uncomment line below to delete all tables and reset database
    # db.drop_all()
    db.create_all()

import webapp.views
