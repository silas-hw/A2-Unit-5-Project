from ast import Assert
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, jsonify
import sqlite3
import hashlib
import time
import datetime

from flaskr.algorithms.algs import validate_isodate

#local imports
from .decorators import *
from .config import Config as config
from .exceptions import *

bp = Blueprint('admin', __name__)

@bp.route('/admin/', methods=['GET'])
@check_loggedin
@check_admin
def admin_portal():
    db_conn = sqlite3.connect(config.db_dir)
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
    db_conn = sqlite3.connect(config.db_dir)

    cursor = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'") # retrieves a list of the names of every table in the database
    database_tables = cursor.fetchall()

    db_conn.close()

    return render_template('/admin/database_view.html', session=session, database_tables=database_tables)

@bp.route('/backend/admin/database/')
@check_loggedin
@check_admin
def database_table():
    table = request.args.get('table')
    field = request.args.get('field')
    query = request.args.get('q')
    search_type = request.args.get('search_type')
    sort_field = request.args.get('sort_field')
    sort_direction = request.args.get('sort_direction')

    db_conn = sqlite3.connect(config.db_dir)

    cursor = db_conn.execute(f'PRAGMA table_info({table})')
    table_headers = cursor.fetchall()
    table_headers = [header[1] for header in table_headers]

    statement = f'SELECT * FROM {table}'
    if query and ';' not in query and ';' not in field:
        search_type = config.search_type_reference[search_type]
        statement += f' WHERE {field}{search_type}{query}'

    if sort_field in table_headers and sort_direction in ('ASC', 'DESC'):
        statement += f' ORDER BY {sort_field} {sort_direction}'

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
    table = request.args.get('table')

    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute(f'PRAGMA table_info({table})')
    table_headers = cursor.fetchall()
    table_headers = [header[1] for header in table_headers]
    db_conn.close()

    return jsonify(table_headers)

###############
# NEWSLETTERS #
###############

@bp.route('/admin/newsletters/')
@check_loggedin
@check_admin
def newsletters():
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT * FROM Newsletter')
    newsletter_list = cursor.fetchall()

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
    try:
        if request.method=='GET':
            return render_template('admin/newsletter_edit.html', action='add', newsletter=[''*10])
        elif request.method=='POST':
            subject = request.form['subject']
            content = request.form['content']
            date_str = request.form['send_date']

            # data validation
            assert date_str, 'Send data cannot be empty'
            assert validate_isodate(date_str), 'Date string format incorrect (direct post request error). It should follow ISO8601'
            
            date = int(time.mktime(datetime.datetime.strptime(request.form['send_date'], config.iso8601).timetuple()))
            
            assert date>int(time.time()), 'Send Date must be in the future'
            assert len(subject) >= 1, 'Subject cannot be empty'
            assert len(content) >= 1, 'Content cannot be empty'

            db_conn = sqlite3.connect(config.db_dir)
            cursor = db_conn.execute('INSERT INTO Newsletter (AccountID, Subject, Content, DateSendEpoch) VALUES (?, ?, ?, ?)', (session['userid'], subject, content, date))
            db_conn.commit()

            db_conn.close()

            return redirect(url_for('admin.newsletters'))
    except AssertionError as err:
        err_msg = err.message
        return render_template('admin/newsletter_edit.html', action='add', newsletter=[''*10], err_msg=err_msg)
        

@bp.route('/admin/newsletter/edit/<newsletter_id>', methods=['POST', 'GET'])
@check_loggedin
@check_admin
def edit_newsletter(newsletter_id):

    try:
        if request.method == 'GET':
            db_conn = sqlite3.connect(config.db_dir)
            cursor = db_conn.execute('SELECT * FROM Newsletter WHERE NewsletterID=?', (newsletter_id,))
            newsletter = cursor.fetchone()
            newsletter_id, account_id, subject, content, date_epoch, sent = newsletter

            date_str = time.strftime(config.iso8601, time.localtime(newsletter[4]))

            db_conn.close()

            return render_template('admin/newsletter_edit.html', action='edit', session=session, newsletter=newsletter, newsletter_id=newsletter_id, date_str=date_str)

        elif request.method == 'POST':
            db_conn = sqlite3.connect(config.db_dir)
            subject = request.form['subject']
            content = request.form['content']
            date_str = request.form['send_date']

            # data validation

            assert date_str, 'Send data cannot be empty'
            assert validate_isodate(date_str), 'Date string format incorrect (direct post request error). It should follow ISO8601'
            
            date = int(time.mktime(datetime.datetime.strptime(request.form['send_date'], config.iso8601).timetuple()))
            
            assert date>int(time.time()), 'Send Date must be in the future'
            assert len(subject) >= 1, 'Subject cannot be empty'
            assert len(content) >= 1, 'Content cannot be empty'
            
            cursor = db_conn.execute('UPDATE Newsletter SET Subject=?, Content=?, DateSendEpoch=?', (subject, content, date))
            db_conn.commit()

            db_conn.close()

            return redirect(url_for('admin.newsletters'))
    except AssertionError as err:
        db_conn = sqlite3.connect(config.db_dir)
        cursor = db_conn.execute('SELECT * FROM Newsletter WHERE NewsletterID=?', (newsletter_id,))
        newsletter = cursor.fetchone()
        newsletter_id, account_id, subject, content, date_epoch, sent = newsletter

        date_str = time.strftime(config.iso8601, time.localtime(newsletter[4]))

        db_conn.close()

        err_msg = err.message

        return render_template('admin/newsletter_edit.html', action='edit', session=session, newsletter=newsletter, newsletter_id=newsletter_id, date_str=date_str, err_msg=err_msg)

@bp.route('/admin/newsletter/<newsletter_id>')
@check_loggedin
@check_admin
def delete_newsletter(newsletter_id):
    return 'Coming Soon', 404