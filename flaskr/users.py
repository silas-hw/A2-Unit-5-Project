from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3

bp = Blueprint('users', __name__)

@bp.route('/account/<account_id>', methods=['GET'])
def account(account_id):
    db_conn = sqlite3.connect('./db/prototype.db')
    
    if account_id not in 
    return redirect(url_for('main.home'))
