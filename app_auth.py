import hashlib, binascii, os
import flask
from flask import request
import functools
import os

import pprint
#import google_auth
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")
app_salt = config.get("auth","FN_FLASK_SECRET_KEY")

app = flask.Blueprint('app_auth', __name__)
app.debug = True

def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)

def is_logged_in():
    #return True if loggedIn in flask.session else False
    return True if 'loggedIn' in flask.session else False
    if flask.session.loggedIn:
        pprint.pprint('Flask session loginhash:')
        pprint.pprint(flask.session.loggedIn)
        return True
    return False

@app.route('/auth/login', methods=['POST'])
@no_cache
def auth_login():
    """Login using provided credentials"""
    pprint.pprint('Got credentials offff')
    pprint.pprint(request.form)
    return "Success %s" % request.form['email']

@app.route('/auth/register', methods=['POST'])
@no_cache
def auth_register_login():
    """Create a login using the supplied credentials in request.form"""
    pprint.pprint('Got credentials offff')
    pprint.pprint(request.form)
    return "Success %s" % request.form['passwd']

def hash_password(password):
    """Hash a password for storing."""
    pwdhash = hashlib.pbkdf2_hmac('sha512', password,
                                app_salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password,
                                app_salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
