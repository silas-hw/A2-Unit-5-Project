from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, jsonify
import sqlite3
import hashlib

#local imports
from .decorators import *
from .config import Config as config

bp = Blueprint('admin', __name__)

@bp.route('/admin/', methods=['GET'])
@check_loggedin
@check_admin
def admin_portal():
    return render_template('/admin/admin_portal.html', session=session)

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
    sort_field = request.args.get('sort_field')
    sort_direction = request.args.get('sort_direction')

    db_conn = sqlite3.connect(config.db_dir)

    cursor = db_conn.execute(f'PRAGMA table_info({table})')
    table_headers = cursor.fetchall()
    table_headers = [header[1] for header in table_headers]

    statement = f'SELECT * FROM {table}'
    if query and ';' not in query and ';' not in field:
        statement += f' WHERE {field}={query}'

    if sort_field in table_headers and sort_direction in ('ASC', 'DESC'):
        statement += f' ORDER BY {sort_field} {sort_direction}'

    print(statement, flush=True)

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
    db_conn.close()
