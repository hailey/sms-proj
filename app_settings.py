#!/usr/bin/env python3
#appsettings.py

import functools
import os
import pprint
import configparser
import flask
import appdb
import google_auth

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")

app = flask.Blueprint('app_settings', __name__)
if app_debug == '1':
    app.debug = True
else:
    app.debug = False

@app.route('/settings')
def appsettings():
    if not google_auth.is_logged_in():
        return flask.render_template('deny.html', denymsg = 'You are not authorized to be here')
    return 'Success you found settings!'