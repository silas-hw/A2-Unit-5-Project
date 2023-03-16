from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

# local imports
from .decorators import *
from .config import Config as config

bp = Blueprint('users', __name__)

@bp.route('/account/<account_id>', methods=['GET'])
@check_loggedin
def account(account_id):
    '''
    Displays information relating to an account of a given account id
    '''

    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT * FROM User WHERE AccountID=?', (account_id))
    res = cursor.fetchone()
    
    if not res:
        db_conn.close()
        return redirect(url_for('main.home'))
    else:
        userid, username, password, email, newsletters, restricted, banknum, banksort, membership, access_level = res
        cursor = db_conn.execute('SELECT Name FROM AccessLevel WHERE AccessID=?', (access_level,))
        access_level = cursor.fetchone()[0]

        db_conn.close()
        return render_template('account.html', userid=res[0], username=res[1], email=res[3], access_level=access_level)

######################
# User Access Levels #
######################

@bp.route('/account/admin/makemod/<account_id>')
@check_loggedin
@check_admin
def user_mod(account_id):
    '''
    Makes the access level of a user equal to that of a moderator
    '''

    db_conn = sqlite3.connect(config.db_dir)
    db_conn.execute('UPDATE User SET AccessLevel=2 WHERE AccountID=?', (account_id,))
    db_conn.close()
    
    return redirect(url_for('users.account', account_id=account_id))

@bp.route('/account/admin/makeadmin/<account_id>')
@check_loggedin
@check_admin
def user_admin(account_id):
    '''
    Makes the access rights of a user equal to that of an admin
    '''

    db_conn = sqlite3.connect(config.db_dir)
    db_conn.execute('UPDATE User SET AccessLevel=3 WHERE AccountID=?', (account_id,))
    db_conn.close()

    return redirect(url_for('users.account', account_id=account_id))

@bp.route('/account/admin/removerights/<account_id>')
@check_loggedin
@check_admin
def user_remove_rights(account_id):
    '''
    Removes all the access rights of a user, returning them to a 'standard' user.
    '''

    db_conn = sqlite3.connect(config.db_dir)
    db_conn.execute('UPDATE User SET AccessLevel=1 WHERE AccountID=?', (account_id,))
    db_conn.close()

    return redirect(url_for('users.account', account_id=account_id))