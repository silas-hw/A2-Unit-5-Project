from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import sqlite3
import time
import datetime

#local imports
from .decorators import *
from .algorithms import *
from .config import Config as config

bp = Blueprint('admin', __name__)

@bp.route('/admin/', methods=['GET'])
@check_loggedin
@check_admin
def admin_portal():
    '''
    The admin homepage. Here the admins can access all the other admin parts of the website.
    '''

    # count the number of accounts that have been created
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SElECT COUNT(AccountID) FROM User')
    num_users = cursor.fetchone()[0]
    db_conn.close()

    return render_template('/admin/admin_portal.html', session=session, num_users=num_users)

############
# DATABASE #
############

@bp.route('/admin/database/')
@check_loggedin
@check_admin
def database_view():
    '''
    This displays a view of the different tables within the database. The actual data is retrieved by
    Javascript on the client-end, being formatted by the database_table() route depending on what
    table, search options and filters the user has chosen.
    '''

    db_conn = sqlite3.connect(config.DB_DIR)

    cursor = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'") # retrieves a list of the names of every table in the database
    database_tables = cursor.fetchall()

    db_conn.close()

    return render_template('/admin/database_view.html', session=session, database_tables=database_tables)

@bp.route('/backend/admin/database/')
@check_loggedin
@check_admin
def database_table():
    '''
    Returns a table from the database as HTML
    '''

    # retrieve all of the URL arguments provided by the user
    table = request.args.get('table')
    field = request.args.get('field')
    query = request.args.get('q')
    search_type = request.args.get('search_type')
    sort_field = request.args.get('sort_field')
    sort_direction = request.args.get('sort_direction')

    db_conn = sqlite3.connect(config.DB_DIR)

    # get all of the fieldnames of the table
    cursor = db_conn.execute(f'PRAGMA table_info({table})')
    table_headers = cursor.fetchall()
    table_headers = [header[1] for header in table_headers]

    # formulate an SQL statement to retrieve data from the table depending on the arguments provided by the user
    statement = f'SELECT * FROM {table}'
    if query and ';' not in query and ';' not in field:
        search_type = config.search_type_reference[search_type]
        statement += f' WHERE {field}{search_type}{query}'

    if sort_field in table_headers and sort_direction in ('ASC', 'DESC'):
        statement += f' ORDER BY {sort_field} {sort_direction}'

    # attempt to retrieve all results from the SQL statement, returning an empty table if it fails
    try:
        cursor = db_conn.execute(statement)
        table_data = cursor.fetchall()
    except sqlite3.OperationalError:
        table_data = []

    db_conn.close()

    return render_template('database/databasetable.html', table_data=table_data, table_headers=table_headers)

@bp.route('/backend/admin/database/fieldnames/')
@check_loggedin
@check_admin
def database_fieldnames():
    '''
    Returns a list of the fieldnames for a database as json data. This route is used exclusively by
    the front-end to dynamically fill some of the dropdown menus.
    '''

    table = request.args.get('table')

    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute(f'PRAGMA table_info({table})')
    table_headers = cursor.fetchall()
    table_headers = [header[1] for header in table_headers]
    db_conn.close()

    return jsonify(table_headers) # jsonify returns the data in the json format which is required by javascript

###############
# NEWSLETTERS #
###############

@bp.route('/admin/newsletters/')
@check_loggedin
@check_admin
def newsletters():
    '''
    Returns a list of newsletters in order of their NewsletterID. 
    '''

    # Retrieve all the newsletters
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT * FROM Newsletter')
    newsletter_list = cursor.fetchall()

    # convert the Unix timestamp of each newsletter into a human-readable date format
    temp_arr = []
    for newsletter in newsletter_list:
        newsletter_id, account_id, subject, content, date_epoch, sent = newsletter

        cursor = db_conn.execute('SELECT Username FROM User WHERE AccountID=?', (account_id,))
        username = cursor.fetchone()[0]

        date = time.strftime('%d/%m/%Y', time.localtime(date_epoch))

        temp_arr.append((newsletter_id, account_id, username, subject, content, date))
    newsletter_list=temp_arr

    db_conn.close()

    return render_template('admin/newsletters.html', session=session, newsletters=newsletter_list)

@bp.route('/admin/newsletter/create/', methods=['POST', 'GET'])
@check_loggedin
@check_admin
def create_newsletter():
    '''
    Either returns a HTML form for admins to create a newsletter, or processes provided data
    for a new newsletter to be created.
    '''

    try:
        if request.method=='GET':
            return render_template('admin/newsletter_edit.html', action='add', newsletter=[''*10], session=session)
        elif request.method=='POST':
            # retrieve data that the user entered into the form
            subject = request.form['subject']
            content = request.form['content']
            date_str = request.form['send_date']

            # data validation
            assert date_str, 'Send data cannot be empty'
            assert validate_isodate(date_str), 'Date string format incorrect (direct post request error). It should follow DATE_FORMAT_ISO8601'
            
            date = int(time.mktime(datetime.datetime.strptime(request.form['send_date'], config.DATE_FORMAT_ISO8601).timetuple()))
            
            assert date>int(time.time()), 'Send Date must be in the future'
            assert len(subject) >= 1, 'Subject cannot be empty'
            assert len(content) >= 1, 'Content cannot be empty'

            db_conn = sqlite3.connect(config.DB_DIR)
            db_conn.execute('INSERT INTO Newsletter (AccountID, Subject, Content, DateSendEpoch) VALUES (?, ?, ?, ?)', (session['userid'], subject, content, date))
            db_conn.commit()

            db_conn.close()

            return redirect(url_for('admin.newsletters'))

    except AssertionError as err:
        # return the newsletter edit page with an error message is validation fails
        err_msg = err
        return render_template('admin/newsletter_edit.html', action='add', newsletter=[''*10], err_msg=err_msg, session=session)
        

@bp.route('/admin/newsletter/edit/<newsletter_id>', methods=['POST', 'GET'])
@check_loggedin
@check_admin
def edit_newsletter(newsletter_id):
    '''
    Either returns a form for a newsletter to be edited (with the fields being
    filled with the newsletters current data), or processes provided data to update
    the data stored under a certain NewsletterID.
    '''

    try:
        if request.method == 'GET':
            # retrieve the data associated with the given Newsletter ID
            db_conn = sqlite3.connect(config.DB_DIR)
            cursor = db_conn.execute('SELECT * FROM Newsletter WHERE NewsletterID=?', (newsletter_id,))
            newsletter = cursor.fetchone()

            # redirect the user if no data is found
            if not newsletter:
                db_conn.close()
                return render_template('errors/error_base.html', error_title='404', error_message="That newsletter doesn't exist :/", session=session)
                
            newsletter_id, account_id, subject, content, date_epoch, sent = newsletter

            # convert the Unix timestamp of the newsletter into a human-readable date format
            date_str = time.strftime(config.DATE_FORMAT_ISO8601, time.localtime(newsletter[4])) 

            db_conn.close()

            return render_template('admin/newsletter_edit.html', action='edit', session=session, newsletter=newsletter, newsletter_id=newsletter_id, date_str=date_str)

        elif request.method == 'POST':
            db_conn = sqlite3.connect(config.DB_DIR)

            # retrieve the data entered in the form
            subject = request.form['subject']
            content = request.form['content']
            date_str = request.form['send_date']

            # data validation
            assert date_str, 'Send data cannot be empty'
            assert validate_isodate(date_str), 'Date string format incorrect (direct post request error). It should follow DATE_FORMAT_ISO8601'
            
            date = int(time.mktime(datetime.datetime.strptime(request.form['send_date'], config.DATE_FORMAT_ISO8601).timetuple()))
            
            assert date>int(time.time()), 'Send Date must be in the future'
            assert len(subject) >= 1, 'Subject cannot be empty'
            assert len(content) >= 1, 'Content cannot be empty'

            cursor = db_conn.execute('SELECT * FROM Newsletter WHERE NewsletterID=?', (newsletter_id,))
            assert cursor.fetchone(), "NewsletterID doesn't exist"
            
            # update the newsletter with the new data
            cursor = db_conn.execute('UPDATE Newsletter SET Subject=?, Content=?, DateSendEpoch=? WHERE NewsletterID=?', (subject, content, date, newsletter_id))
            db_conn.commit()

            db_conn.close()

            return redirect(url_for('admin.newsletters'))

    except AssertionError as err:
        # The error message can't be displayed by simply using a redirect call, so previous code needs to be repeated (unfortunately)
        db_conn = sqlite3.connect(config.DB_DIR)
        cursor = db_conn.execute('SELECT * FROM Newsletter WHERE NewsletterID=?', (newsletter_id,))
        newsletter = cursor.fetchone()
        newsletter_id, account_id, subject, content, date_epoch, sent = newsletter

        date_str = time.strftime(config.DATE_FORMAT_ISO8601, time.localtime(newsletter[4]))

        db_conn.close()

        err_msg = err

        return render_template('admin/newsletter_edit.html', action='edit', session=session, newsletter=newsletter, newsletter_id=newsletter_id, date_str=date_str, err_msg=err_msg)

@bp.route('/admin/newsletter/<newsletter_id>')
@check_loggedin
@check_admin
def delete_newsletter(newsletter_id):
    '''
    Removes the row in the database associated with a certain NewsletterID
    '''

    # check if the newsletter actually exists
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT * FROM Newsletter WHERE NewsletterID=?', (newsletter_id,))
    res = cursor.fetchone()
    
    # if the newsletter doesn't exit then redirect the user
    if not res:
        db_conn.close()
        return render_template('errors/error_base.html', error_title='404', error_message="That newsletter doesn't exist :/", session=session)

    # delete the newsletter
    db_conn.execute('DELETE FROM Newsletter WHERE NewsletterID=?', (newsletter_id,))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('admin.newsletters'))