#!/usr/bin/env python3

import time
import datetime
import pprint
import configparser
import json
import re
import appdb, appsms
#from flask import Flask, render_template, request
import flask
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import google_auth
import callback_sms

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")

app = flask.Flask(__name__)
app.secret_key = config.get("auth","FN_FLASK_SECRET_KEY")

app.register_blueprint(google_auth.app)
app.register_blueprint(callback_sms.app)

if app_debug == '1':
    app.debug = True
else:
    app.debug = False

@app.route('/')
def index():
    if not google_auth.is_logged_in():
        return 'You are not currently logged in.'
    user_info = google_auth.get_user_info()
    indbRes = appdb.isUserinDB(user_info['id'])
    if indbRes:
        pprint.pprint(indbRes)
        refreshtoken = google_auth.getRefreshToken()
        if not refreshtoken:
            return "Error with your refresh token"
        
        userid = appdb.getUserIDfromGoogleID(user_info['id'])
        if not userid:
            return 'You are not currently logged in.'
        
        rows = appdb.getDIDsbyAccount(userid)
        return flask.render_template('index.html',
                                    name = user_info['name'],
                                    picture = user_info['picture'],
                                    dids = rows)
    else:
        # Lets setup the user
        refreshtoken = google_auth.getRefreshToken()
        
        if user_info['verified_email'] == True:
            verifiedVar = True
        else:
            verifiedVar = False
            
        appdb.setNewUser(user_info['id'], refreshtoken, user_info['name'], user_info['email'], verifiedVar)
        return flask.render_template('landing.html',
                                    name = user_info['name'],
                                    picture = user_info['picture'])


@app.route('/single/<int:number>', methods=['GET'])
def manageSingleSMS(number):
    if not google_auth.is_logged_in():
        return flask.render_template('deny.html')
    
    refreshtoken = google_auth.getRefreshToken()
    
    userid = appdb.getUserIdFromRT(refreshtoken)
    result = appdb.authIdforDID(userid,number)
    
    prettynum = appsms.prettyPhone(number)
    if appdb.validateFrom(int(number)) and result:
        return flask.render_template('single.html',srcnumber = number, prettynum = prettynum)
    else:
        return flask.render_template('notvalid.html', srcnumber = number, prettynum = prettynum)

@app.route('/getNumber/<int:did>',methods=['GET'])
def getNumMessages(number):
    #This gets the mssages based on the provided from or two DID
    if not google_auth.is_logged_in():
        return flask.render_template('deny.html')
    
    refreshtoken = google_auth.getRefreshToken()
    userid = appdb.getUserIdFromRT(refreshtoken)
    result = appdb.authIdforDID(userid,number)
    smslog = appdb.getNumSMSLog(number,10)
    if not result:
        return flask.render_template('deny.html', 'Invalid ID for DID')
    
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
        return flask.render_template('deny.html')
    
    message = flask.request.form['message']
    fromDid = flask.request.form['fromdid']
    targetDid = flask.request.form['targetdid']
    
    refreshtoken = google_auth.getRefreshToken()
    userid = appdb.getUserIdFromRT(refreshtoken)
    result = appdb.authIdforDID(userid,fromDid)
    
    if userid != result:
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
        returndata = json.dumps({"msg" : message, "fromdid" : fromDid, 'targetdid' : targetDid,})
    return returndata

@app.route('/testAjax')
def testAjax():
    return json.dumps({"msg" : 'Success!'})

@app.route('/pp')
def PrivacyPolicy():
    pprint.pprint(flask.session)
    return flask.render_template('pp.html')

@app.route('/tos')
def tos():
    return flask.render_template('tos.html')

if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("8890")
    )
    
