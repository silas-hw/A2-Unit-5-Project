from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3
import hashlib

# local imports
from .decorators import *
from .config import Config as config
from .algorithms import *

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

################
# Edit Account #
################

@bp.route('/account/edit/', methods=['POST', 'GET'])
@check_loggedin
def edit_account():
    if request.method=='GET':
        return render_template('accounts/edit_account.html', session=session)
    elif request.method=='POST':
        try:
            # perform data validation to ensure that all the required data is provided in the form
            assert 'username' in request.form, 'username must be in form'
            assert 'email' in request.form, 'email must be in form'
            assert 'oldpassword' in request.form, 'oldpassword must be in form'
            assert 'newpassword' in request.form, 'newpassword must be in form'
            assert 'newpassword2' in request.form, 'newpassword2 must be in form'

            # assign the provided data to variables
            username = request.form['username']
            email = request.form['email']
            oldpassword = request.form['oldpassword']
            newpassword = request.form['newpassword']
            newpassword2 = request.form['newpassword2']
            newsletter = 1 if "newsletter" in request.form else 0 

            oldpassword_hash = hashlib.sha256(oldpassword.encode('utf-8')).hexdigest() # hash/encrypt the old password with sha256 to hexadecimal

            # data validation
            db_conn = sqlite3.connect(config.db_dir)
            cursor = db_conn.execute('SELECT * FROM User WHERE AccountID=? AND Password=?', (session['userid'], oldpassword_hash))
            res = cursor.fetchone()

            assert res, 'Old Password Incorrect'

            cursor = db_conn.execute('SELECT * FROM User WHERE (username=? OR email=?) AND AccountID!=?', (username, email, session['userid']))
            res = cursor.fetchall()

            assert len(res)==0, 'Email or Username already in use'

            assert len(username)>3, 'Username is too short'
            assert check_email(email), 'Invalid email format'
            assert newpassword!=newpassword.upper(), 'Password must contain a lowercase letter'
            assert newpassword!=newpassword.lower(), 'Password must contain an uppercase letter'
            assert any(char.isdigit() for char in newpassword), 'Password must contain a number'
            assert any(not char.isalnum() and not char==' ' for char in newpassword), 'Password must contain a special character'
            assert newpassword==newpassword2, 'Passwords do not match'

            newpassword_hash = hashlib.sha256(newpassword.encode('utf-8')).hexdigest() # hash/encrypt the new password with sha256 to hexadecimal

            # update the information stored about the user in the database to match the data provided
            db_conn.execute('UPDATE User SET username=?, email=?, password=?, ReceiveNewsletter=? WHERE AccountID=?', (username, email, newpassword_hash, newsletter, session['userid']))
            db_conn.commit()

            # update the session to match the users new credentials
            session['username'] = username
            session['email'] = email

            return redirect(url_for('users.account', account_id=session['userid']))

        except AssertionError as err:
            return render_template('accounts/edit_account.html', session=session, err_msg=err)


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