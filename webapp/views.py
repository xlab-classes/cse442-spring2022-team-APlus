from webapp import app, login_manager, ALLOWED_EXTENSIONS
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


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


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
            im = Image.open('/Users/jingjingchi/Downloads/cse442-spring2022-team-APlus/default_profile.jpeg')
            data = io.BytesIO()
            filetype = 'jpeg'
            im.save(data, filetype)
            encoded_img_data = base64.b64encode(data.getvalue()).decode('utf-8')
            print("fffff",len(encoded_img_data))
            #pro= Profile(email,encoded_img_data)
            user = Accounts(email, hashed_password)
            db.session.add(user)
           #db.session.add(pro)
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
        im = Image.open(app.config['UPLOAD_FOLDER']+'/'+filename)
        data = io.BytesIO()
        filetype = filename.split('.')[1]
        im.save(data, filetype)
        encoded_img_data = base64.b64encode(data.getvalue())
        print(len(encoded_img_data.decode('utf-8'))) #<class 'str'>
        return render_template('profile.html',  img_data=encoded_img_data.decode('utf-8'))


@app.route('/listing', methods=['GET', 'POST'])
@login_required
def listings():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        files = request.files.getlist("files")
        listing = Listings(user_id=current_user.id, title=title, description=description)
        db.session.add(listing)
        db.session.commit()
        for file in files:
            if file and allowed_file(file.filename):
                file_extension = '.' + file.filename.split('.')[-1]
                random_filename = str(uuid4()) + file_extension
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))
                file = Files(post_id=listing.id, file_path=random_filename)
                db.session.add(file)
        db.session.commit()
        return redirect(url_for('listings'))

    return render_template('listing.html', listings=display_listings())



def display_listings():
    output = ""
    active_listings = reversed(Listings.query.all())
    for listing in active_listings:
        listing_owner = Accounts.query.filter_by(id=listing.user_id).first()
        output += "<p>{0} - {1}</p><p>{2}</p>".format(listing.title, listing_owner.email, listing.description)
        listing_photos = Files.query.filter_by(post_id=listing.id)
        for photos in listing_photos:
            output += "<img src={0}>".format(app.config['UPLOAD_FOLDER'].split('webapp')[1] + photos.file_path)
            output += "<a href=\" /listing/delete/"+ str(listing.id )+" \" class=\"btn btn-outline-danger btn-sm\">Delete Post</a>"
    return output

@app.route('/listing/delete/<int:id>')
def delete_post(id):
    post_to_delete = Listings.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        return render_template('listing.html', listings=display_listings())
    except:
        return render_template('listing.html', listings=display_listings())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
