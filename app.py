#!/usr/bin/env python3

import time
import datetime
import pprint
import configparser
import json
import re
import flask
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import appdb, appsms, app_settings, app_auth
import google_auth
import callback_sms

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")

app = flask.Flask(__name__)
app.secret_key = config.get("auth","FN_FLASK_SECRET_KEY")

app.register_blueprint(google_auth.app)
app.register_blueprint(callback_sms.app)
app.register_blueprint(app_settings.app)
app.register_blueprint(app_auth.app)

loginMsg = "You are not logged in."

if app_debug == '1':
    app.debug = True
else:
    app.debug = False

@app.route('/')
def index():
    '''This is the root index. If not logged in it displays homepage.html'''
    if not app_auth.is_logged_in():
        return flask.render_template('homepage.html', loggedin = False)

    logId = flask.session['loginID']
    indbRes = appdb.isUserinDB(logId)
    try:
        if google_auth.is_logged_in():
            user_info = google_auth.get_user_info()

        elif loggedIn in flask.session == True:
            user_info['name'] = flask.session['name']
            user_info['picture'] = flask.session['picture']
            user_info['verified_email'] = flask.session['verified_email']
        else:
            user_info = False
    except NameError:
        user_info = False
        indbRes = False

    if indbRes and user_info['name'] == '':
        if app_debug == '1':
            pprint.pprint(indbRes)
        #refreshtoken = google_auth.getRefreshToken()
        #if not refreshtoken:
        #    return flask.render_template('error.html', denymsg = 'Error with your refresh token.', loggedin = False)

        #userid = appdb.getUserIDfromGoogleID(user_info['id'])
        #if not userid:
        #    return flask.render_template('error.html', denymsg = 'You are not currently logged in.', loggedin = False)

        rows = appdb.getDIDsbyAccount(logId)
        return flask.render_template('index.html',
                                    name = user_info['name'],
                                    picture = user_info['picture'],
                                    dids = rows,
                                    loggedin = True)
    else:
        # Lets setup the user
        if google_auth.is_logged_in():
            refreshtoken = google_auth.getRefreshToken()
            if user_info['verified_email'] <= 1:
                verifiedVar = True
                appdb.setNewUser(user_info['id'], refreshtoken, user_info['name'], user_info['email'],1)
                return flask.render_template('landing.html',
                                             user_info = user_info, loggedin = False)
            else:
                #This means they aren't verified.
                verifiedVar = False
                return flask.render_template('deny.html',denymsg = 'Your google account does not have a verified email. This is required to use this service.', loggedin = False)
        else:
            return flask.render_template('deny.html',denymsg = 'Your google account does not have a Refresh Token. This is required to use this service.', loggedin = False)

@app.route('/landing')
def landingPage():
    '''This renders the landing page'''
    user_info = google_auth.get_user_info()
    if user_info:
        loggedin = True
    else:
        loggedin = False
    return flask.render_template('landing.html', user_info = user_info, loggedin = loggedin)

@app.route('/single/<int:number>', methods=['GET'])
def manageSingleSMS(number):
    '''This renders a view for a single SMS number and its associated messages'''
    if not app_auth.is_logged_in():
        return flask.render_template('deny.html',denymsg = loginMsg, loggedin = False)

    #refreshtoken = google_auth.getRefreshToken()
    googleid = google_auth.getGoogleId()
    userid = appdb.getUserIDfromGoogleID(googleid)
    result = appdb.authIdforDID(userid,number)

    prettynum = appsms.prettyPhone(number)
    if appdb.validateFrom(int(number)) and result:
        return flask.render_template('single.html',srcnumber = number, prettynum = prettynum, loggedin = True)
    else:
        return flask.render_template('notvalid.html', srcnumber = number, prettynum = prettynum, loggedin = True)

@app.route('/getNumber/<int:number>',methods=['GET'])
def getNumMessages(number):
    #This gets the mssages based on the provided from or two DID
    if not google_auth.is_logged_in():
        return json.dumps({'error': 'Unable to send SMS, you are not logged in'})

    #refreshtoken = google_auth.getRefreshToken()
    googleid = google_auth.getGoogleId()
    userid = appdb.getUserIDfromGoogleID(googleid)
    result = appdb.authIdforDID(userid,number)
    smslog = appdb.getNumSMSLog(number,10)
    if not result:
        return json.dumps({'error': 'You are not allowed to use the requested DID'})

    i = 0
    msgjson = ""
    for line in smslog:
        prettyto = appsms.prettyPhone(line[7])
        prettyfrom = appsms.prettyPhone(line[6])
        if i >= 1:
            msgjson = msgjson + ',' + json.dumps({'to':prettyto,'from':prettyfrom,'body':line[9],'timestamp': line[4],'status': line[10]})
        else:
            msgjson =  json.dumps({'to':prettyto,'from':prettyfrom,'body':line[9],'timestamp': line[4], 'status': line[10]})
        i += 1


    msgArrayJson = '['+msgjson +']'
    return msgArrayJson

@app.route('/submitMessage', methods=['POST'])
def submitMessage():
    #This is to submit a message.

    if not google_auth.is_logged_in():
        return json.dumps({'error': 'Unable to send SMS'})

    message = flask.request.form['message']
    fromDid = flask.request.form['fromdid']
    targetDid = flask.request.form['targetdid']
    #user_info = google_auth.get_user_info()
    #refreshtoken = google_auth.getRefreshToken()
    googleid = google_auth.getGoogleId()
    userid = appdb.getUserIDfromGoogleID(googleid)
    result = appdb.authIdforDID(userid,fromDid)

    if userid != result:
        if app_debug == '1':
            pprint.pprint(userid)
            pprint.pprint(result)
        return json.dumps({'error': 'Unauthorized UserID of ' + str(userid) + " and DID id of " + str(result) + " and fromDID " + str(fromDid)})

    if appdb.validateFrom(fromDid) == False:
        return json.dumps({'error': 'Unauthorized source phone number.'})

    uglyphone = appsms.uglyPhone(targetDid)

    #pprint.pprint('Got ' + message + ',' + fromDid)
    msg_id = appsms.sendsms(uglyphone,fromDid,message)
    if msg_id == False: #This sends the sms!
        returndata = json.dumps({'error': 'Unable to send SMS'})
    else:
        msgTS = time.strftime("%Y-%m-%dT%H:%m:%SZ")
        appdb.logsms_db(msg_id, msgTS, 'outbound', uglyphone, fromDid, 0.0040, 'pending', message, result)
        returndata = json.dumps({"msg" : message, "fromdid" : fromDid, 'targetdid' : targetDid})
    return returndata

@app.route('/testAjax')
def testAjax():
    return json.dumps({"msg" : 'Success!'})

@app.route('/inbox')
def inbox():
    if not app_auth.is_logged_in():
        return 'You are not logged in'
    loginId = flask.session.loggedIn
    results = appdb.getSMSbyAccount(loginId,10)
    return results

@app.route('/launch')
def launchPage():
    if google_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    if app_debug == '1':
        pprint.pprint(loggedin)
        pprint.pprint("loggedin")
    return flask.render_template('launch.html',loggedin=loggedin)

@app.route('/pp')
def PrivacyPolicy():
    if app_debug == '1':
        pprint.pprint(flask.session)
    if google_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    return flask.render_template('pp.html',loggedin=loggedin)

@app.route('/tos')
def tos():
    if google_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    return flask.render_template('tos.html',loggedin=loggedin)

@app.route('/about')
def about():
    if google_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    return flask.render_template('about.html',loggedin=loggedin)

if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("8890")
    )
