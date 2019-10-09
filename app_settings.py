#!/usr/bin/env python3
#app_settings.py

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
        return flask.render_template('deny.html', denymsg = 'You are not authorized to be here', loggedin = False)
    user_info = google_auth.get_user_info()
    refreshtoken = google_auth.getRefreshToken()
    if not refreshtoken:
        return flask.render_template('error.html', denymsg = 'Error with your refresh token', loggedin = False)
    userid = appdb.getUserIDfromGoogleID(user_info['id'])
    if not userid:
        return flask.render_template('error.html', denymsg = 'You are not currently logged in.', loggedin = False)

    rows = appdb.getDIDsbyAccount(userid)
    dbEmail = appdb.getInfobyEmail(user_info['email'])
    return flask.render_template('settings.html',
                                name = user_info['name'],
                                email = user_info['email'],
                                dids = rows,
                                loggedin = True)