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
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT Rating FROM WebsiteRating WHERE AccountID=?', (session['userid'],))
    user_rating = cursor.fetchone() 
    user_rating = str(user_rating) if user_rating else ''

    if request.method == 'GET':
        # return the rating form, inserting the users current rating if they have already submitted one
        db_conn.close()
        return render_template('review.html', session=session, user_rating=user_rating)
    elif request.method == 'POST':
        # set a boolean to if the user has currently created a rating or not
        rating_present = True if user_rating != '' else False
        user_rating = request.form['rating']

        # update the rating stored in the WebsiteRating table is the user has already created one
        if rating_present:
            db_conn.execute('UPDATE WebsiteRating SET Rating=? WHERE AccountID=?', (user_rating, session['userid']))
            db_conn.commit()

        # create a new entry in the WebsiteRating tablei if the user has already created a rating
        else:
            db_conn.execute('INSERT INTO WebsiteRating (AccountID, Rating) VALUES (?, ?)', (session['userid'], user_rating))
            db_conn.commit()

        db_conn.close()
        return redirect(url_for('main.dashboard'))
        

