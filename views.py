from webapp import app, login_manager, ALLOWED_EXTENSIONS, mail
from flask import request, make_response, render_template, redirect, url_for, flash
from webapp.models import db, Accounts, Listings, Files
import bcrypt
import os
from werkzeug.utils import secure_filename
from PIL import Image
import base64
import io
from uuid import uuid4
from flask_login import login_user, login_required, current_user, logout_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Message

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


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
        if not stored_email or not Accounts.query.filter_by(email=email).first().password:
            msg = "Login failed. Incorrect username or password."
            return render_template("login.html", msg=msg)
        stored_password_hash = Accounts.query.filter_by(email=email).first().password.encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
            if not stored_email.is_verified:
                token = serializer.dumps(stored_email.email)
                message = Message("Verify Your Account", sender=("CSE442 - Team A+", "cse442aplus@gmail.com"),
                                  recipients=[stored_email.email])
                message.body = "Visit {0}verify/{1} this link to verify your account.".format(request.host_url, token)
                mail.send(message)
                msg = "Unverified account. Click on the verification link in your email. " \
                      "If needed, a new link has been sent to your address."
            else:
                msg = "Login successful!"
                login_user(stored_email)
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
        if email_query:
            msg = "Email In Use"
        elif len(email.split('@')) == 2 and len(email.split('.')) == 2 and "@buffalo.edu" in email:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = Accounts(email, hashed_password)
            token = serializer.dumps(user.email)
            message = Message("Verify Your Account", sender=("CSE442 - Team A+", "cse442aplus@gmail.com"),
                              recipients=[user.email])
            message.body = "Visit {0}verify/{1} this link to verify your account.".format(request.host_url, token)
            mail.send(message)
            msg = "Account created for {0}. Check your email and verify your account.".format(user.email)
        else:
            msg = "Invalid UB Email"
    return render_template('signup.html', msg=msg)


@app.route('/verify/<token>')
def verify_account(token):
    if request.method == 'GET':
        try:
            email = serializer.loads(token, max_age=3600)
            user = Accounts.query.filter_by(email=email).first()
            if user.is_verified:
                return "Your account has already been verified.".format(email)
            else:
                user.verify_account()
                return "Your account has been verified!".format(email)
        except SignatureExpired:
            return "Your verification link has expired. Visit the login page to request a new link."
        except:
            return "Invalid verification link"


@app.route('/upload', methods=['GET', 'POST'])
def profile():
    if request.method == "GET":
        print()
        return render_template("profile.html")
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        # flash('Image successfully uploaded and displayed below')
        im = Image.open(app.config['UPLOAD_FOLDER'] + '/' + filename)
        data = io.BytesIO()
        filetype = filename.split('.')[1]
        print(filetype)
        im.save(data, filetype)
        encoded_img_data = base64.b64encode(data.getvalue())
        return render_template('profile.html', img_data=encoded_img_data.decode('utf-8'))


@app.route('/listing', methods=['GET', 'POST'])
@login_required
def listings():
    if request.method == 'POST':

        # post for creating listing was not used
        # post for filtering was done instead
        if request.form['title'] == None:
            filterList = request.form['filter']

            # output = filter_listings(filterList)
            #return render_template('listing.html', listings=filter_listings(filterList))
            return redirect(url_for('filter', filters=filterList))
        ##################################

        # else
        #code for display all listings and recently added ones
        title = request.form['title']
        description = request.form['description']
        files = request.files.getlist("files")
        valid_images = []
        for file in files:
            if file and allowed_file(file.filename):
                valid_images.append(file)
        if len(valid_images) == 0:
            return redirect(url_for('listings'))
        listing = Listings(user_id=current_user.id, title=title, description=description)
        db.session.add(listing)
        db.session.commit()
        for file in valid_images:
            file_extension = '.' + file.filename.split('.')[-1]
            random_filename = str(uuid4()) + file_extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))
            file = Files(post_id=listing.id, file_path=random_filename)
            db.session.add(file)
        db.session.commit()
        return redirect(url_for('listings'))

    flash("HELOOWORLD", "message")
    return render_template('listing.html', listings=display_listings())


@app.route('/filterList', methods=['GET', 'POST'])
@login_required
def filter_list(fil=None):

    if request.method == 'POST':

        keyword = request.form['fil']

        return render_template('filterList.html', listings=filter_listings(keyword))

    return render_template('filterList.html', listings=filter_listings(fil))


@app.route('/delete_profile')
@login_required
def delete():
    files_obj = Files.query.filter_by(id=current_user.id).first()
    listings_obj = Listings.query.filter_by(id=current_user.id).first()
    account_obj = Accounts.query.filter_by(id=current_user.id).first()
    if files_obj:
        db.session.delete(files_obj)
    if listings_obj:
        db.session.delete(listings_obj)
    if account_obj:
        db.session.delete(account_obj)
    db.session.commit()
    flash("User Deleted Successfully.")
    return render_template("/signup.html")


def display_listings():
    output = ""
    active_listings = reversed(Listings.query.all())
    for listing in active_listings:
        listing_owner = Accounts.query.filter_by(id=listing.user_id).first()
        output += "<p>{0} - {1}</p><p>{2}</p>".format(listing.title, listing_owner.email, listing.description)
        listing_photos = Files.query.filter_by(post_id=listing.id)
        for photos in listing_photos:
            output += "<img src={0}>".format(app.config['UPLOAD_FOLDER'].split('webapp')[1] + photos.file_path)
    return output


def filter_listings(keyword):
    all_listings = reversed(Listings.query.all())
    filtered_listings = filtering(all_listings, keyword)
    output = display_set(filtered_listings)

    return output


def filtering(input_list, keyword):
    filtered_list = []

    if keyword is None:
        return input_list
    for listing in input_list:
        if keyword in listing.description:
            filtered_list.append(listing)

    # Task test output check
    for listing in filtered_list:
        print(listing.description)
    return filtered_list


def display_set(list_set):
    output = ''
    for listing in list_set:
        listing_owner = Accounts.query.filter_by(id=listing.user_id).first()
        output += "<p>{0} - {1}</p><p>{2}</p>".format(listing.title, listing_owner.email, listing.description)
        listing_photos = Files.query.filter_by(post_id=listing.id)
        for photos in listing_photos:
            output += "<img src={0}>".format(app.config['UPLOAD_FOLDER'].split('webapp')[1] + photos.file_path)

    # Task test output check
    print(output)

    return output


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS