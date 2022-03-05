from webapp import app, login_manager
from flask import request, render_template, redirect,url_for,flash
from webapp.models import db, Accounts, Listings, Files
import bcrypt
import os
from werkzeug.utils import secure_filename
from PIL import Image
import base64
import io
from uuid import uuid4
from flask_login import login_user, login_required, current_user, logout_user


@login_manager.user_loader
def load_user(user_id):
    return Accounts.query.get(int(user_id))


@app.route('/', methods=['GET'])
def home():
    if current_user.is_authenticated:
        return 'Hello {0}!'.format(current_user.email)
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        stored_email = Accounts.query.filter_by(email=email).first()
        if not stored_email:
            msg = "Login failed. Incorrect username or password."
            return render_template('login.html', msg=msg)
        stored_password_hash = Accounts.query.filter_by(email=email).first().password.encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
            msg = "Login successful!"
            login_user(stored_email)
            return render_template('profile.html', msg=msg)
        else:
            msg = "Login failed. Incorrect username or password."
    return render_template('login.html', msg=msg)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


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


@app.route('/listing', methods=['GET', 'POST'])
@login_required
def listings():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        files = request.files.getlist("files")
        listing = Listings(title=title, description=description)
        db.session.add(listing)
        db.session.commit()
        for file in files:
            random_filename = str(uuid4()) + ".jpg"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))
            file = Files(post_id=listing.id, file_path=random_filename)
            db.session.add(file)
        db.session.commit()

    return render_template('listing.html', listings="Hello!")
