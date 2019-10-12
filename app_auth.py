import hashlib, binascii, os
import pprint
import google_auth
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")
app_salt = config.get("auth","FN_FLASK_SECRET_KEY")

app = flask.Blueprint('app_auth', __name__)

def is_logged_in():
    if google_auth.is_logged_in():
        return True
    return False

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
