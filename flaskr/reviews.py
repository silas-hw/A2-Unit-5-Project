from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

# local imports
from .decorators import *
from .config import Config as config

bp = Blueprint('reviews', __name__)

@bp.route('/review/', methods=['POST', 'GET'])
@check_loggedin
def review():

    # retrieve the users current rating if they have made one at all
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT Rating FROM WebsiteRating WHERE AccountID=?', (session['userid'],))
    user_rating = cursor.fetchone() 
    user_rating = str(user_rating) if user_rating else ''

    if request.method == 'GET':
        # return the rating form, inserting the users current rating if they have already submitted one
        db_conn.close()
        return render_template('review.html', session=session, user_rating=user_rating)
    elif request.method == 'POST':
        # insert a new rating into the WebsiteRating table if the user has not already submitted one, 
        # or update the users existing rating if they have
        rating_present = True if user_rating != '' else False
        user_rating = request.form['rating']

        if rating_present:
            db_conn.execute('UPDATE WebsiteRating SET Rating=? WHERE AccountID=?', (user_rating, session['userid']))
            db_conn.commit()

        else:
            db_conn.execute('INSERT INTO WebsiteRating (AccountID, Rating) VALUES (?, ?)', (session['userid'], user_rating))
            db_conn.commit()

        db_conn.close()
        return redirect(url_for('main.dashboard'))
        

