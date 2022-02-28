from webapp import app
from flask import request, render_template
from webapp.models import Accounts, db
import bcrypt


@app.route('/', methods=['GET'])
def home():
    return 'Hello World!'


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
            db.session.add(user)
            db.session.commit()
            msg = "Account created for {0}".format(email)
        else:
            msg = "Invalid UB Email"
    return render_template('signup.html', msg=msg)
