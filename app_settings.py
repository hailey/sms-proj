#!/usr/bin/env python3
#app_settings.py

import functools
import os
import pprint
import configparser
import json
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
    '''This function pulls some information and then renders the settings or error template'''
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

@app.route('/checkUsername/<username>', methods=['GET'])
def checkUsername(username):
    '''This function returns json error if username exists and json 'available'
     if it is avaiable.'''
    data = appdb.isUserExist(username)
    if data:
        return json.dumps({'error': 'Username already exists, please choose another.'})
    return json.dumps({'name': 'Available'})

@app.route('/createUser', methods=['POST'])
def createUser():
    '''Create the rest of the db entry for the user'''
    username = flask.request.form['username']
    password = flask.request.form['password']
    email = flask.request.form['email']
    user_info = google_auth.get_user_info()
    if appdb.isUserExist(username):
         return json.dumps({'error': 'Username already exists. Please choose another.'})

    if appdb.getInfobyEmail(email):
        return json.dumps({'error': 'A user has already been registered with this information. Maybe you want to try recovering a password?'})

    passwd = app_auth.hash_password(password.encode('ascii'))
    res = appdb.finalizeNewUser(email, username, passwd)
    if app_debug == '1':
        pprint.pprint('Updating email, username, passwd' + email )
    if res:
        return json.dumps({'msg': 'Success!'})
    return json.dumps({'error': 'There is an error in processing the request.'})
