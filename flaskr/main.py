from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

bp = Blueprint('main', __name__)

@bp.route('/home/', methods=['GET'])
def home():
    return render_template('home.html', session=session)