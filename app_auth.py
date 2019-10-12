import hashlib, binascii, os
import google_auth
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")
salt = config.get("auth","FN_FLASK_SECRET_KEY")

def is_logged_in():
    if google_auth.is_logged_in():
        return True
    return False

def hash_password(password):
    """Hash a password for storing."""
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = salt
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
