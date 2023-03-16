from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import atexit

# local imports
from .auth import bp as auth_bp
from .main import bp as main_bp
from .users import bp as users_bp
from .documents import bp as documents_bp
from .admin import bp as admin_bp

from .tasks import scheduler

def create_app(test_config=None):
    '''
    Constructs the application from all of the blueprints provided. 
    This is used by flask when passing the 'flask run' command in the commandline.
    '''

    # create a flask app
    app = Flask(__name__)

    app.secret_key = 'secretekey'
    
    # register all of the imported blueprints to the application
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(admin_bp)

    # start the scheduler so that emails can be sent
    scheduler.start()
    atexit.register(scheduler.shutdown) # stops the scheduler when the program closes (i.e. when the server stops running)

    return app