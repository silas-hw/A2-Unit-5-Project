from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

from .auth import bp as auth_bp
from .main import bp as main_bp
from .users import bp as users_bp
from .documents import bp as documents_bp

def create_app(test_config=None):
    app = Flask(__name__)

    app.secret_key = 'secretekeygoeshere'
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(documents_bp)

    return app