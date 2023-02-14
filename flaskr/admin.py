from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
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

@bp.route('/admin/database/')
@check_loggedin
@check_admin
def database_view():
    return render_template('/admin/database_view.html', session=session)

