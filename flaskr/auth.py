from os import access
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3
import hashlib
import time

# local imports
from .decorators import *
from .algorithms import *
from .config import Config as config
from .exceptions import *

bp = Blueprint('auth', __name__)

@bp.route('/login/', methods=['GET', 'POST'])
@check_loggedout
def login():
    '''
    Used for a user to 'log in' to an account they have already created using their
    email and password.
    '''

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:

        # assign the data provided in the post request to variables
        email = request.form['email']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest() # instantly hash/encrypt the password with sha256 to hexadecimal

        # create an sqlite connection and check if the entered account details exist and match within the database
        db_conn = sqlite3.connect(config.db_dir)
        cursor = db_conn.execute('SELECT AccountID, Username, AccessLevel FROM User WHERE Email=? AND Password=?', (email, password_hash))
        res = cursor.fetchone()
        db_conn.close()

        # if the entered details were correct, create a session and redirect the user to the home page
        # 'if res' will return True if res contains any data, which will only be true itself if
        # the username and password combination entered by the user is correct
        if res:
            account_id, username, access_level = res
            session['loggedin'] = True
            session['userid'] = account_id
            session['username'] = username
            session['email'] = email
            session['access'] = access_level
            session['largefont'] = False

            return redirect(url_for('main.home'))
        else:
            # reload the login page but with an error message
            # err_msg will be inserted into the login.html template by jinja2
            return render_template('/auth/login.html', err_msg='Incorrect Username or Password')

    return render_template('/auth/login.html', err_msg='')

@bp.route('/logout/', methods=['GET'])
@check_loggedin
def logout():
    '''
    Used for a user to 'log out' from their account if they are already logged in.
    '''

    # remove all the user details from the current session if they are already loggedin (i.e. 'log them out')
    [session.pop(key) for key in list(session.keys())]
    
    return redirect(url_for('main.home'))

@bp.route('/register/', methods=['GET', 'POST'])
@check_loggedout
def register():
    '''
    Allows the user to create a new account and access the features of the website that require an account
    to use.
    '''
    
    try:
        if request.method == 'GET':
            return render_template('/auth/register.html', err_msg='')

        elif request.method == 'POST':
            # if required data hasn't been entered return an error message to the user
            if 'username' not in request.form or 'email' not in request.form or 'password' not in request.form:
                raise InvalidFormData('Please enter all data')

            # assign variables to the data provided in the post request
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            # validation
            if len(username)<=1 or not check_email(email):
                raise InvalidFormData('Invalid data provided')

            # forms can only send string data, so here the newsletter field is converted into an integer boolean
            # Whilst we could technically just cast it using the int method, this way
            # prevents any hiccups if something other than 1 or 0 is sent by assuming it to be 0
            newsletter = 1 if "newsletter" in request.form else 0 

            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

            # create an sqlite connection to check if the account already exists
            db_conn = sqlite3.connect(config.db_dir)
            cursor = db_conn.execute('SELECT AccountID FROM User WHERE Email=? OR Username=?', (email, username))
            res = cursor.fetchone()
            
            # if the account already exists, reload the register page but with an error message
            if res:
                raise InvalidFormData('Username and/or Email already in use')
            
            # insert the new account information into the User table within the database
            db_conn.execute('INSERT INTO User (username, email, password, RecieveNewsletter) VALUES (?, ?, ?, ?)', (username, email, password_hash, newsletter))
            db_conn.commit()

            # create a session for the user, automatically logging them in upon account creation
            userid = db_conn.execute('SELECT AccountID FROM User WHERE Email=?', (email,)).fetchone()[0]
            db_conn.close()

            session['loggedin'] = True
            session['userid'] = userid
            session['username'] = username
            session['email'] = email
            session['largefont'] = False
            session['access'] = 1

            return redirect(url_for('main.home'))
    except InvalidFormData as err:
        err_msg = err.message
        return render_template('/auth/register.html', err_msg=err_msg)
