from flask import Flask
from webapp.models import db
import os
from dotenv import load_dotenv
from flask_login import LoginManager

load_dotenv()
app = Flask(__name__)

UPLOAD_FOLDER = 'webapp/static/uploads'
sql_database = 'mysql+pymysql://{0}:{1}@oceanus.cse.buffalo.edu/{2}'.format(os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'))
app.config['SECRET_KEY'] = 'mySecretKey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = sql_database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
with app.app_context():
    # Uncomment line below to delete all tables and reset database
    # db.drop_all()
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

import webapp.views
