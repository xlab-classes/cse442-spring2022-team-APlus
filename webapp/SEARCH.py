from flask import Flask
from flask import flash
from flask import render_template, redirect, url_for, request, session
import config
from sqlalchemy import or_, and_

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rooms.sqlite3'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

class Rooms(db.Model):
    #id = db.Column('id', db.Integer, primary_key = True)
    room_name = db.Column(db.String(20), primary_key = True)
    city = db.Column(db.String(200), nullable=False)
    neighbor = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self, room_name, city, neighbor,price):
        self.room_name = room_name
        self.city = city
        self.neighbor = neighbor
        self.price = price



@app.before_first_request
def create_tables():
    db.create_all()



@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['room_name'] :
          flash('Please enter all the fields', 'error')
      else:
         room = Rooms(request.form['room_name'], request.form['city'],request.form['neighbor'], request.form['price'])

         db.session.add(room)
         db.session.commit()
         flash('Record was successfully added')
         msg = "Record successfully added"
         return render_template("result.html",msg = msg)
   return render_template('new.html')

@app.route('/finding')
def index():
    return render_template('postPage.html')



@app.route('/search/')
def search():
    c = request.args.get('city')
    n = request.args.get('neighbor')
    if c != '' and n != '':
        ques = Rooms.query.filter(
            and_(
                Rooms.city == c,

                Rooms.neighbor == n
            ))
    elif c == '' and n != '':
        ques = Rooms.query.filter(
            and_(

                Rooms.neighbor == n
            ))
    elif c != '' and n == '':
        ques = Rooms.query.filter(
            and_(

                Rooms.city == c
            ))
    return render_template('search.html', rooms=ques)
if __name__ == '__main__':
   app.run(debug = True)

