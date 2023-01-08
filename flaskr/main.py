from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

from .decorators import *

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
@bp.route('/home/', methods=['GET'])
@bp.route('/landingpage/', methods=['GET'])
@check_loggedout
def home():
    '''
    returns the homepage to users who are not logged in and redirects logged in users to their dashboard
    '''
    db_conn = sqlite3.connect('./db/prototype.db')
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
    return render_template('dashboard.html', session=session)