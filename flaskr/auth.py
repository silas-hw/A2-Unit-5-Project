from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3
import hashlib

bp = Blueprint('auth', __name__)

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        db_conn = sqlite3.connect('./db/prototype.db')
        cursor = db_conn.execute('SELECT rowid, Username FROM users WHERE Email=? AND Password=?', (email, password_hash))
        res = cursor.fetchone()
        db_conn.close()

        if res:
            session['loggedin'] = True
            session['userid'] = res[0]
            session['username'] = res[1]
            session['email'] = email

            return redirect(url_for('main.home'))
        else:
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
        cursor = db_conn.execute('SELECT rowid FROM users WHERE Email=? OR Username=?', (email, username))
        res = cursor.fetchone()

        if res:
            return render_template('register.html', err_msg='Username and/or Email already in use')
        
        db_conn.execute('INSERT INTO users (username, email, password, newsletter) VALUES (?, ?, ?, ?)', (username, email, password_hash, newsletter))
        db_conn.commit()
        userid = db_conn.execute('SELECT rowid FROM users WHERE email=?', (email,)).fetchone()[0]
        db_conn.close()

        session['loggedin'] = True
        session['userid'] = userid
        session['username'] = username
        session['email'] = email

        return redirect(url_for('main.home'))