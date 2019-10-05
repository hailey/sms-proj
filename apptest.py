import functools
import json
import os
import configparser

import flask

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import google_auth

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")


app = flask.Flask(__name__)
app.secret_key = config.get("auth","FN_FLASK_SECRET_KEY")

app.register_blueprint(google_auth.app)

@app.route('/')
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"

    return 'You are not currently logged in.'

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8020")
    )