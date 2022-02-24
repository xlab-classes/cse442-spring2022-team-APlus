from webapp import app
from flask import request, render_template
from webapp.models import Accounts


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
            msg = "Valid UB Email"
        else:
            msg = "Invalid UB Email"
    return render_template('signup.html', msg=msg)
