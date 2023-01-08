from flask import session, redirect, url_for
import functools

def check_loggedin(func):
    '''
    This can be used to 'wrap' any route in the website to ensure only logged in users can access it
    '''
    @functools.wraps(func)
    def wrapper():
        if 'loggedin' not in session:
            return redirect(url_for('main.home'))
        return func()
    return wrapper

def check_loggedout(func):
    '''
    This can be used to 'wrap' any route in the website to ensure only logged in users can access it
    '''
    @functools.wraps(func)
    def wrapper():
        if 'loggedin' in session:
            return redirect(url_for('main.dashboard'))
        return func()
    return wrapper