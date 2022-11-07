from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
@bp.route('/home/', methods=['GET'])
@bp.route('/landingpage/', methods=['GET'])
def home():
    if 'loggedin' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html', session=session)

@bp.route('/', methods=['GET'])
@bp.route('/dashboard/', methods=['GET'])
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('main.home'))
    return render_template('dashboard.html', session=session)