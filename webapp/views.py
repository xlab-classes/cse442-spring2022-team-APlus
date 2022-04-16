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
session = {}


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
        Username = request.form['Username']
        stored_email = Accounts.query.filter_by(email=email).first()
        stored_Username = Accounts.query.filter_by(Username=Username).first()
        if not stored_email or not Accounts.query.filter_by(email=email).first().password or not stored_Username:
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
        Username = request.form['Username']
        email_query = Accounts.query.filter_by(email=email).first()
        if email_query:
            msg = "Email In Use"
        elif len(email.split('@')) == 2 and len(email.split('.')) == 2 and "@buffalo.edu" in email:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = Accounts(email, hashed_password, Username)
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
@login_required
def profile():
    if request.method == 'POST':
        id = current_user.id
        file1 = Accounts.query.get_or_404(id)
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_extension = filename.split('.')[1]
            random_filename = str(uuid4()) + '.' + file_extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))
            file1.profile = random_filename
            # file.profile = random_filename
            img = profile(id=current_user.id, file_path=random_filename)
            db.session.add(img)
            db.session.commit()
            return render_template('profile.html')
    else:
        return render_template('profile.html')


@app.route('/edit', methods=['GET', 'POST'])
def dashboard():
    id = current_user.id
    name_to_update = Accounts.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.Username = request.form['Username']
        db.session.commit()
        return render_template('profile.html')


@app.route('/listing', methods=['GET', 'POST'])
@login_required
def listings():
    session["previous_url"] = url_for("listings")
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
        listing = Listings(user_id=current_user.id, title=title, description=description, likes=0)
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
    return render_template("signup.html")


def display_listings():
    output = ""
    active_listings = reversed(Listings.query.all())
    print(active_listings)
    for listing in active_listings:
        print(listing)
        listing_owner = Accounts.query.filter_by(id=listing.user_id).first()
        output += "<p>{0} - {1}</p><p>{2}</p><p>Likes: {3}</p>".format(listing.title, listing_owner.email,
                                                                       listing.description, listing.likes)
        output += "<a href=\" /listing/delete/" + str(
            listing.id) + " \" class=\"btn btn-outline-danger btn-sm\">Delete Post</a>"
        listing_photos = Files.query.filter_by(post_id=listing.id)
        for photos in listing_photos:
            output += "<img src={0} height=500 width=500><p></p>".format(
                app.config['UPLOAD_FOLDER'].split('webapp')[1] + photos.file_path)
            output += "<a href=\" /listing/like/" + str(
                listing.id) + " \" class=\"btn btn-outline-danger btn-sm\">Like/Unlike Post</a><p></p>"
            output += "<a href=\" /listing/save/" + str(
                listing.id) + " \" class=\"btn btn-outline-danger btn-sm\">Save Post</a>"
    return output





@app.route("/view_saved")
@login_required
def view_saved():
    session["previous_url"] = url_for("view_saved")
    cur_saved_posts = reversed(Accounts.query.filter_by(id=current_user.id).first().saved_posts)
    output = ""
    active_listings = cur_saved_posts
    for listing_id in active_listings:
        listing = Listings.query.filter_by(id=listing_id).first()
        listing_owner = Accounts.query.filter_by(id=listing.user_id).first()
        output += "<p>{0} - {1}</p><p>{2}</p><p>Likes: {3}</p>".format(listing.title, listing_owner.email,
                                                                       listing.description, listing.likes)
        output += "<a href=\" /listing/delete/" + str(
            listing.id) + " \" class=\"btn btn-outline-danger btn-sm\">Delete Post</a>"
        listing_photos = Files.query.filter_by(post_id=listing.id)
        for photos in listing_photos:
            output += "<img src={0} height=500 width=500><p></p>".format(
                app.config['UPLOAD_FOLDER'].split('webapp')[1] + photos.file_path)
            output += "<a href=\" /listing/like/" + str(
                listing.id) + " \" class=\"btn btn-outline-danger btn-sm\">Like/Unlike Post</a><p></p>"
            output += "<a href=\" /listing/save/" + str(
                listing.id) + " \" class=\"btn btn-outline-danger btn-sm\">Save Post</a>"
    return render_template('saved.html', saved=output)


@app.route('/listing/save/<int:id>')
@login_required
def save_post(id):
    # listing = Listings(user_id=current_user.id, title=title, description=description, likes=0)
    # post_to_save = Listings.query.filter_by(id=id).first()
    user_that_is_saving = Accounts.query.filter_by(id=current_user.id).first()
    try:
        if id in user_that_is_saving.saved_posts:
            user_that_is_saving.saved_posts.remove(id)
            flash("Post unsaved!")
            db.session.commit()
        else:
            user_that_is_saving.saved_posts.append(id)
            flash("Post saved!")
            db.session.commit()
    except Exception as e:
        print("Error while saving the post. \n")
        print(e)
    return redirect(session["previous_url"])


@app.route('/listing/like/<int:id>')
@login_required
def like_post(id):
    post_to_like = Listings.query.filter_by(id=id).first()
    user_that_is_liking = Accounts.query.filter_by(id=current_user.id).first()
    try:
        if id in user_that_is_liking.liked_posts:
            post_to_like.likes -= 1
            user_that_is_liking.liked_posts.remove(id)
            db.session.commit()
            print("post successfully unliked.\n Post ID {} now has {} likes".format(id, post_to_like.likes))
        else:
            post_to_like.likes += 1
            user_that_is_liking.liked_posts.append(id)
            db.session.commit()
            print("post successfully liked.\n Post ID {} now has {} likes".format(id, post_to_like.likes))
    except Exception as e:
        print("error while liking/disliking the post: \n")
        print(e)
        pass
    return redirect(session["previous_url"])


@app.route('/listing/delete/<int:id>')
@login_required
def delete_post(id):
    print("here1")
    # id = current_user.id
    post_to_delete = Listings.query.get(id)
    print('here2')
    if id == post_to_delete.user_id:
        try:
            for user in Accounts.query.all():
                if id in user.saved_posts:
                    user.saved_posts.remove(id)
                    print("deleting from saved")
                if id in user.liked_posts:
                    user.liked_posts.remove(id)
                    print("deleting from likes")
            db.session.delete(post_to_delete)
            db.session.commit()
        except Exception as e:
            print("Exception while deleting post:\n")
            print(e)
        print("here")
    return redirect(session["previous_url"])


@app.route('/chat/', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'GET':
        return render_template('chat.html', chat_history='unhandled. TODO')
    elif request.method == 'POST':
        recipient_email = request.form['email']
        recipient = Accounts.query.filter_by(email=recipient_email).first()
        if recipient and recipient.id != current_user.id:
            message = request.form['message']
            Msg(current_user.id, recipient.id, message)
    return redirect(url_for('chat'))


# Test endpoint to create new accounts without email verification. Password does not support special characters
#
# Usage:
# localhost:<port>/devtool/create_account?email=<email>&password=<password>&username=<username>

@app.route('/devtool/create_account')
def test_account():
    if request.method == "GET":
        args = request.args
        email = args['email']
        password = args['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = Accounts(email, hashed_password)
        user.verify_account()
        return "TEST ACCOUNT CREATED - " + email + ":" + password


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
