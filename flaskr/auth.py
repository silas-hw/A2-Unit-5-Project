from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3
import hashlib

bp = Blueprint('auth', __name__)

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:

        # assign the data provided in the form to variables
        email = request.form['email']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest() # instantly hash/encrypt the password with sha256 to hexadecimal

        # create an sqlite connection and check if the entered account details exist and match within the database
        db_conn = sqlite3.connect('./db/prototype.db')
        cursor = db_conn.execute('SELECT AccountID, Username FROM User WHERE Email=? AND Password=?', (email, password_hash))
        res = cursor.fetchone()
        db_conn.close()

        # if the entered details were correct, create a session and redirect the user to the home page
        if res:
            account_id, username = res
            session['loggedin'] = True
            session['userid'] = account_id
            session['username'] = username
            session['email'] = email

            return redirect(url_for('main.home'))
        else:
            # reload the login page but with an error message
            # err_msg will be inserted into the login.html template by jinja
            return render_template('login.html', err_msg='Incorrect Username or Password')
    
    if 'loggedin' in session:
        return redirect(url_for('main.home'))

    return render_template('login.html', err_msg='')

@bp.route('/logout/', methods=['GET'])
def logout():
    if 'loggedin' in session:
        session.pop('loggedin')
        session.pop('userid')
        session.pop('username')
        session.pop('email')
    
    return redirect(url_for('main.home'))

@bp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', err_msg='')
    elif request.method == 'POST':
        if 'loggedin' in session:
            return redirect(url_for('main.home'))

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        newsletter = 1 if request.form['newsletter'] == "1" else 0
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        db_conn = sqlite3.connect('./db/prototype.db')
        cursor = db_conn.execute('SELECT AccountID FROM User WHERE Email=? OR Username=?', (email, username))
        res = cursor.fetchone()

        if res:
            return render_template('register.html', err_msg='Username and/or Email already in use')
        
        db_conn.execute('INSERT INTO User (username, email, password, RecieveNewsletter) VALUES (?, ?, ?, ?)', (username, email, password_hash, newsletter))
        db_conn.commit()
        userid = db_conn.execute('SELECT AccountID FROM User WHERE Email=?', (email,)).fetchone()[0]
        db_conn.close()

        session['loggedin'] = True
        session['userid'] = userid
        session['username'] = username
        session['email'] = email

        return redirect(url_for('main.home'))