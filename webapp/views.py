from webapp import app, login_manager, ALLOWED_EXTENSIONS, mail
from flask import request, render_template, redirect, url_for, flash
from webapp.models import db, Accounts, Listings, Files, Msg
import bcrypt
import os
from werkzeug.utils import secure_filename
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


@app.route('/login/', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        if('@' in email):
            stored_email = Accounts.query.filter_by(email=email).first()
        else:
            if (Accounts.query.filter_by(Username=email).first() == None):
                msg = "Login failed. Incorrect username or password. "
                return render_template("login.html", msg=msg)
            email = Accounts.query.filter_by(Username=email).first().email
            stored_email = Accounts.query.filter_by(email=email).first()
     
        if (not stored_email or not Accounts.query.filter_by(email=email).first().password) :
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
                return render_template('profile.html')
        else:
            msg = "Login failed. Incorrect username or password."
    return render_template('login.html', msg=msg)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    msg = ""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        Username = request.form['Username']
        email_query = Accounts.query.filter_by(email=email).first()
        Username_query = Accounts.query.filter_by(Username=Username).first()
        if email_query:
            msg = "Email In Use"
        if Username_query:
            msg = "Username In Use"
        elif len(email.split('@')) == 2 and len(email.split('.')) == 2 and "@buffalo.edu" in email:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = Accounts(email, hashed_password,Username)
            token = serializer.dumps(user.email)
            message = Message("Verify Your Account", sender=("CSE442 - Team A+", "cse442aplus@gmail.com"),
                              recipients=[user.email])
            message.body = "Visit {0}verify/{1} this link to verify your account.".format(request.host_url, token)
            mail.send(message)
            msg = "Account created for {0}. Check your email and verify your account.".format(user.email)
        else:
            msg = "Invalid UB Email"
    return render_template('signup.html', msg=msg)
  
  
@app.route('/verify/<token>/')
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


@app.route('/upload/', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        id = current_user.id
        file1 = Accounts.query.get_or_404(id)
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_extension = filename.split('.')[1]
            random_filename = str(uuid4()) +'.'+ file_extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))
            file1.profile = random_filename 
            db.session.commit()
            return render_template('profile.html')
    else:
        return render_template('profile.html')
@app.route('/edit', methods=['GET', 'POST'])
def dashboard():
    id = current_user.id
    name_to_update = Accounts.query.get_or_404(id)
    if request.method == "POST":
        new_Username  = request.form['Username']
        if new_Username != "":
            Username_query = Accounts.query.filter_by(Username=new_Username).first()
            if Username_query and new_Username != name_to_update.Username :
                flash("Username in use")
            else:
                name_to_update.Username = request.form['Username']
                db.session.commit()
        return render_template('profile.html')


@app.route('/listing/', methods=['GET', 'POST'])
@login_required
def listings():
    if request.method == 'POST':
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

    return render_template('listing.html', listings=display_listings())


@app.route('/delete_profile/')
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
    return render_template("signup.html")


def display_listings():
    output = ""
    active_listings = reversed(Listings.query.all())
    for listing in active_listings:
        listing_owner = Accounts.query.filter_by(id=listing.user_id).first()
        output += "<p>{0} - {1}</p><p>{2}</p>".format(listing.title, listing_owner.email, listing.description)
        output += "<a href=\" /listing/delete/"+ str(listing.id )+" \" class=\"btn btn-outline-danger btn-sm\">Delete Post</a>"
        listing_photos = Files.query.filter_by(post_id=listing.id)
        for photos in listing_photos:
            output += "<img src={0}>".format(app.config['UPLOAD_FOLDER'].split('webapp')[1] + photos.file_path)
    return output

  
@app.route('/listing/delete/<int:id>/')
@login_required
def delete_post(id):
    id = current_user.id
    post_to_delete = Listings.query.get_or_404(id)
    if id == post_to_delete.user_id:
         try:
             db.session.delete(post_to_delete)
             db.session.commit()
             return redirect(url_for('listings'))
         except:
             return redirect(url_for('listings'))


@app.route('/message/', methods=['GET'])
@login_required
def conversation():
    users = Accounts.query.all()
    user_list = ""
    for user in users:
        if user.id != current_user.id:
            user_list += "<a href='{0}'>{1}</a><br/>".format(user.id, user.email)
    return render_template('message_user_directory.html', user_list=user_list)


@app.route('/message/<int:recipient_id>/', methods=['GET', 'POST'])
@login_required
def message(recipient_id):
    recipient = Accounts.query.get_or_404(recipient_id)
    if request.method == 'POST':
        message = request.form['message']
        Msg(current_user.id, recipient.id, message)
        return redirect(url_for('message', recipient_id=recipient_id))
    sender_msgs = Msg.query.filter(Msg.sender_id == current_user.id, Msg.recipient_id == recipient_id)
    receiver_msgs = Msg.query.filter(Msg.sender_id == recipient_id, Msg.recipient_id == current_user.id)
    msg_history = sender_msgs.union(receiver_msgs).order_by(Msg.id)
    messages = ""
    for msg in msg_history:
        if msg.sender_id == current_user.id:
            messages += "{0}: {1}<br/>".format(current_user.email, msg.message)
        else:
            messages += "{0}: {1}<br/>".format(recipient.email, msg.message)
    return render_template('message.html', recipient_id=recipient_id, recipient_email=recipient.email, message_history=messages)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
