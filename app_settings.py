#!/usr/bin/env python3
#app_settings.py

import functools
import os
import pprint
import configparser
import flask

import appdb, app_auth
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
    if not app_auth.is_logged_in():
        return flask.render_template('deny.html', denymsg = "I don't know who you are so I can't help you with your user settings. :(", loggedin = False)
    user_info = google_auth.get_user_info()
    refreshtoken = google_auth.getRefreshToken()

    if not refreshtoken:
        return flask.render_template('error.html', denymsg = 'Error with your refresh token.', loggedin = False)
    userid = appdb.getUserIDfromGoogleID(user_info['id'])
    if not userid:
        return flask.render_template('error.html', denymsg = 'You are not currently logged in.', loggedin = False)

    rows = appdb.getDIDsbyAccount(userid)
    accountInfo = appdb.getInfobyEmail(user_info['email'])
    # userDBInfo.getInfobyE
    pprint.pprint(accountInfo)
    return flask.render_template('settings.html',
                                user_info = user_info,
                                account_info = accountInfo,
                                dids = rows,
                                loggedin = True)
