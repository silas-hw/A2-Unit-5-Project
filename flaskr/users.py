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
        access_name = cursor.fetchone()[0]

        # create an sqlite connection and retrieve a list of the currently logged in users documents
        cursor = db_conn.execute('SELECT DocumentName, Description, DocumentID FROM Document WHERE AccountID=? AND Public=1 LIMIT 3', (session['userid'],))
        documents = cursor.fetchall()

        db_conn.close()
        return render_template('accounts/account.html', userid=res[0], username=res[1], email=res[3], access_level=access_level, access_name=access_name, public_documents=documents)

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

##################
# Delete Account #
##################

@bp.route('/account/delete', methods=['POST', 'GET'])
@check_loggedin
def delete_account():
    if request.method == 'GET':
        return render_template('accounts/delete_account.html')
    elif request.method == 'POST':
        userid = session['userid']
        db_conn = sqlite3.connect(config.db_dir)

        # delete every database entry associated with the users account id
        db_conn.execute('DELETE FROM WebsiteRating WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM DocumentLike WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM MembershipPayment WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM Page WHERE PageID=(SELECT PageID FROM Page WHERE DocumentID IN (SELECT DocumentID FROM Document WHERE AccountID=?))', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM Document WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM DocumentShare WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM DocumentComment WHERE CommentID IN (SELECT CommentID FROM Comment WHERE AccountID=?)', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM CommunityPostComment WHERE CommentID IN (SELECT CommentID FROM Comment WHERE AccountID=?)', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM Comment WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM User WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM CommunityPost WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.execute('DELETE FROM CommunityPostLike WHERE AccountID=?', (userid,))
        db_conn.commit()

        db_conn.close()

        return redirect(url_for('auth.logout'))