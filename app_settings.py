#!/usr/bin/env python3
#app_settings.py

import functools
import os
import pprint
import configparser
import json
import flask

import appdb, app_auth

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
    if flask.session.get('loginid'):
        user_info = appdb.getUserInfo(flask.session['email'],flask.session['loginid'])
        loggedin = True
    else:
        user_info = False
        indbRes = False
        return flask.render_template('deny.html', denymsg = "I don't know who you are so I can't help you with your user settings. :(", loggedin = False)
    if user_info:
        rows = appdb.getDIDsbyAccount(user_info[0])
        pprint.pprint(user_info)
        accountInfo = appdb.getInfobyEmail(user_info[2])

        pprint.pprint(accountInfo)
    else:
        return 'error';
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
    #user_info = google_auth.get_user_info()
    if appdb.isUserExist(username):
         return json.dumps({'error': 'Username already exists. Please choose another.'})

    data = appdb.getInfobyEmail(email)
    if data[4] >= 2: # This should be 2 if a user is already registered. If its less than two it oughta be okay.
        return json.dumps({'error': 'A user has already been registered with this information. Maybe you want to try recovering a password?'})
    if data[9]:
        return json.dumps({'error': 'A password has already been registered with this information. Maybe you want to try recovering a password?'})

    passwd = app_auth.hash_password(password.encode('ascii'))
    res = appdb.finalizeNewUser(email, username, passwd)
    if app_debug == '1':
        pprint.pprint('Updating email, username, passwd' + email )
    if res:
        return json.dumps({'msg': 'Success!'})
    return json.dumps({'error': 'There is an error in processing the request.'})
