from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

# local imports
from .decorators import *
from .config import Config as config

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
@bp.route('/home/', methods=['GET'])
@bp.route('/landingpage/', methods=['GET'])
@check_loggedout
def home():
    '''
    returns the homepage to users who are not logged in and redirects logged in users to their dashboard
    '''
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT Rating, AccountID FROM WebsiteRating ORDER BY Rating DESC LIMIT 5')
    ratings_temp=cursor.fetchall()
    ratings=[]
    for rating in ratings_temp:
        cursor = db_conn.execute('SELECT Username FROM User WHERE AccountID=?', (rating[1],))
        username = cursor.fetchone()[0]
        rating = [rating[0], username]
        ratings.append(rating)
    
    db_conn.close()
    return render_template('home.html', session=session, ratings=ratings)

@bp.route('/', methods=['GET'])
@bp.route('/dashboard/', methods=['GET'])
@check_loggedin
def dashboard():
    '''
    returns the dashboard to users who are logged in and redirects not logged in users to the homepage
    '''

    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT DocumentName, Description, AccountID, DocumentID FROM Document WHERE Public=1 ORDER BY DocumentID DESC LIMIT 20')
    res = cursor.fetchall()
    recent_docs=[]
    for doc in res:
        cursor = db_conn.execute('SELECT Username FROM User WHERE AccountID=?', (doc[2],))
        username = cursor.fetchone()[0]

        recent_docs.append({
            'username':username,
            'title':doc[0],
            'description':doc[1],
            'document_id':doc[3]
        })

    return render_template('dashboard.html', session=session, recent_docs=recent_docs)

@bp.route('/changefont/')
@check_loggedin
def changefont():
    '''
    Increases or decreases the font size of every element depending
    on the users current preference.
    '''
    session['largefont'] = not session['largefont']
    return redirect(url_for('main.dashboard'))

