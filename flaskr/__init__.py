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
from .reviews import bp as reviews_bp

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
    app.register_blueprint(reviews_bp)

    # register error handlers
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, server_error)
    app.register_error_handler(502, bad_gateway)
    app.register_error_handler(503, service_unavailable)

    # start the scheduler so that emails can be sent
    scheduler.start()
    atexit.register(scheduler.shutdown) # stops the scheduler when the program closes (i.e. when the server stops running)

    return app

def page_not_found(e):
    return render_template('errors/error_base.html', error_title='404', error_message="Sorry mate, that URL isn't correct", session=session)

def server_error(e):
    return render_template('errors/error_base.html', error_title='500', error_message="Oops... the server ran into a problem", session=session)

def bad_gateway(e):
    return render_template('errors/error_base.html', error_title='502', error_message='Error: bad gateway', session=session)

def service_unavailable(e):
    return render_template('errors/error_base.html', error_title="503", error_message=":/ Service Unavailable. The server was not able to handle your request; It may be overloaded or down for maintenance.", session=session)

