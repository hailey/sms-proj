import hashlib
import flask
from flask import request, redirect
import binascii
# from passlib.hash
import functools
import os
import appdb
import pprint
# import google_auth
import configparser

salt = os.urandom(32)
config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app", "debug")
app_salt = config.get("auth", "FN_FLASK_SECRET_KEY")
login_redirect = "/"

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
    if flask.session.get('loginid'):
        pprint.pprint('Flask session loginhash:')
        pprint.pprint(flask.session.get('loginid'))
        if appdb.verify_id(
            flask.session.get('email'),
                flask.session.get('loginid')) is True:
            return True
        return False
    return False


def verify_login(email, password):
    result = appdb.verify_login(email, password)
    if result:
        return True
    return False


@app.route('/auth/login', methods=['POST'])
@no_cache
def auth_login():
    """Login using provided credentials"""
    # pprint.pprint('Got credentials offff')
    # pprint.pprint(request.form)
    if appdb.verify_login(
        request.form['email'],
            hash_password(request.form['passwd'].encode('ascii'))):
        pprint.pprint("got variables")
        uniqueID = appdb.generate_id(request.form['email'])
        flask.session['loggedin'] = True
        flask.session['loginid'] = uniqueID
        flask.session['account_id'] = appdb.getAccountId(uniqueID)
        flask.session['email'] = request.form['email']
        flask.session['password'] = request.form['passwd']
        return "/"
    return "error"
    # return login_redirect


@app.route('/auth/register', methods=['POST'])
@no_cache
def auth_register_login():
    """Create a login using the supplied credentials in request.form"""
    # pprint.pprint('Got credentials offff')
    # pprint.pprint(request.form)
    return "DISABLED"


@app.route('/auth/updatepw', methods=['POST'])
@no_cache
def auth_updatepw():
    '''This takes three post variables to match the old password then match two
    passwords forms then update password if it all checks out.'''

    if not is_logged_in():
        return "error"
    if flask.session['loginid']:
        user_info = appdb.getUserInfo(
            flask.session['email'], flask.session['loginid'])

    passzero = request.form['passwdzero']
    passone = request.form['passwdone']
    orighash = hash_password(passzero.encode('ascii'))
    newhash = hash_password(passone.encode('ascii'))
    if (appdb.updatePass(user_info[0], orighash, newhash)):
        return '200'
    return "error"


@app.route('/auth/logout')
@no_cache
def auth_logout():
    flask.session.clear()
    return redirect('/')


def hash_password(password):
    """Hash a password for storing."""
    pwdhash = hashlib.pbkdf2_hmac(
        'sha512', password, app_salt.encode('ascii'), 100000)
    # hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    pwdhash = hashlib.pbkdf2_hmac(
        'sha512', provided_password, app_salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
