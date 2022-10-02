from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

bp = Blueprint('users', __name__)

@bp.route('/account/', methods=['GET'])
def account():
    return redirect(url_for('main.home'))
