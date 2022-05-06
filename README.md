# Team A+

## Setup Instructions
1. Clone the GitHub repo: `git clone <github_repo_url>`
2. cd into the cloned repo folder
3. Create a screen session: `screen -S <screen_name>`
4. Create the python virtual environment with the following commands:
    1. `virtualenv <virtualenv_name>`
    2. `source <virtualenv_name>/bin/activate.csh`
5. Install all necessary packages
    1. Upgrade pip: `pip install --upgrade pip`
    2. Install all requirements with `pip install -r requirements.txt`.
        1. NOTE: If that doesn't work, run the following command to install all packages manually: `pip install flask flask_sqlalchemy flask_login python-dotenv flask_mail pymysql bcrypt`
6. Create the .env file with the command: `nano .env`
7. Add the database and email server credentials into the .env file and save the changes
8. Run the web application: `python run.py`
9. Disconnect from the screen to allow the application to run in the background: `ctrl-a + d`