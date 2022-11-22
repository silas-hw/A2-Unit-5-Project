from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

bp = Blueprint('users', __name__)

@bp.route('/account/<account_id>', methods=['GET'])
def account(account_id):
    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT * FROM User WHERE AccountID=?', (account_id))
    res = cursor.fetchone()
    
    if len(res)==0:
        return redirect(url_for('main.home'))
    else:
        cursor = db_conn.execute('SELECT Name FROM AccessLevel WHERE AccessID=?', (res[7],))
        access_level = cursor.fetchone()[0]
        return render_template('account.html', userid=res[0], username=res[1], email=res[3], access_level=access_level)