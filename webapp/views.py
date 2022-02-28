from fileinput import filename
from webapp import app
from flask import request, render_template, redirect,url_for,flash
from webapp.models import Accounts, db
import bcrypt
import os
from werkzeug.utils import secure_filename
from PIL import Image
import base64
import io
@app.route('/', methods=['GET'])
def home():
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        stored_password_hash = Accounts.query.filter_by(email=email).first().password.encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
            msg = "Login successful!"
            return render_template('profile.html', msg=msg)
        else:
            msg = "Login failed. Incorrect username or password."
    return render_template('login.html', msg=msg)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        email_query = Accounts.query.filter_by(email=email).first()
        #print("password----", email)
        #print("password: {}".format(email_query.password))
       # print(Accounts.query.filter_by(email=email).first())
        if email_query:
            msg = "Email In Use"
        elif len(email.split('@')) == 2 and len(email.split('.')) == 2 and "@buffalo.edu" in email:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = Accounts(email, hashed_password)
            db.session.add(user)
            db.session.commit()
            msg = "Account created for {0}".format(email)
        else:
            msg = "Invalid UB Email"
    return render_template('signup.html', msg=msg)

 #change this to the directory where you want save the user profile image   
app.config['UPLOAD_FOLDER'] = "/Users/jingjingchi/Downloads/cse442-spring2022-team-APlus/static/uploads"
@app.route('/upload', methods=['POST'])
def profile():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        #flash('Image successfully uploaded and displayed below')
        im = Image.open(app.config['UPLOAD_FOLDER']+'/'+filename)
        data = io.BytesIO()
        filetype = filename.split('.')[1]
        print(filetype)
        im.save(data, filetype)
        encoded_img_data = base64.b64encode(data.getvalue())
        return render_template('profile.html',  img_data=encoded_img_data.decode('utf-8'))
    
    

@app.route('/display/<filename>')
def display_image(filename):
    print("fffff")
    print('display_image filename: ' + filename)
    print("ddd",url_for('static', filename='uploads/' + filename))
    return redirect(url_for("static",filename='upload_image/' + filename), code=301)    
#   return render_template('profile.html', filename=filename)