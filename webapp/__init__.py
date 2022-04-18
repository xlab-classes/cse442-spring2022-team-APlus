from flask import Flask
from webapp.models import db
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_mail import Mail



load_dotenv()
app = Flask(__name__)


UPLOAD_FOLDER = 'webapp/static/uploads/'
sql_database = 'mysql+pymysql://{0}:{1}@oceanus.cse.buffalo.edu/{2}?charset=utf8mb4'.format(os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'))
app.config['SECRET_KEY'] = 'mySecretKey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['SQLALCHEMY_DATABASE_URI'] = sql_database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('SMTP_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('SMTP_PASSWORD')
# app.config['MAIL_USERNAME'] =SMTP_USERNAME
# app.config['MAIL_PASSWORD'] = SMTP_PASSWORD

app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
with app.app_context():
    # Uncomment line below to delete all tables and reset database
    # db.drop_all()
    db.create_all() # this creates the database based on what is in models.py i think

login_manager = LoginManager()
login_manager.init_app(app)

import webapp.views
