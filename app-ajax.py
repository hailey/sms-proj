#!/usr/bin/env python3

import time
import datetime
import pprint
import configparser
import json
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
    if google_auth.is_logged_in():
        pprint.pprint("Getting userinfo on /")
        user_info = google_auth.get_user_info()
        pprint.pprint("Gotem!")
        return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><div><img src="' + user_info['picture'] + '" alt="Self Photo" /></div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
    return 'You are not currently logged in.'

@app.route('/single/<int:number>', methods=['GET'])
def manageSingleSMS(number):
    if not google_auth.is_logged_in():
        return flask.render_template('deny.html')
    
    if appdb.validateFrom(int(number)):
        return flask.render_template('single.html',srcnumber = number)
    else:
        return flask.render_template('notvalid.html', srcnumber = number)

@app.route('/getMessages',methods=['GET'])
def getMessages():
    if not google_auth.is_logged_in():
        return flask.render_template('deny.html')
    smslog = appdb.getAllSMSLog(10)
    epprint.pprint(smslog)
    msgjson = ""
    i = 0
    for line in smslog:
        #pprint.pprint(line)
        if i >= 1:
            msgjson = msgjson + ',' + json.dumps({'to':line[7],
                              'from':line[6],
                              'body':line[9],
                              'timestamp': line[4]})
        else:
            msgjson =  json.dumps({'to':line[7],
                              'from':line[6],
                              'body':line[9],
                              'timestamp': line[4]})
        i += 1
        
    
    msgArrayJson = '['+msgjson +']'
    return msgArrayJson

@app.route('/getNumber/<int:did>',methods=['GET'])
def getNumMessages(did):
    if not google_auth.is_logged_in():
        return flask.render_template('deny.html')
    #This gets the mssages based on the provided from or two DID
    smslog = appdb.getNumSMSLog(did,10)
    #pprint.pprint(smslog)
    i = 0
    msgjson = ""
    for line in smslog:
        #pprint.pprint(line)
        if i >= 1:
            msgjson = msgjson + ',' + json.dumps({'to':line[7],
                              'from':line[6], # :)
                              'body':line[9],
                              'timestamp': line[4],
                              'status': line[10]})
        else:
            msgjson =  json.dumps({'to':line[7],'from':line[6],'body':line[9],'timestamp': line[4], 'status': line[10]})
        i += 1
        
    
    msgArrayJson = '['+msgjson +']'
    return msgArrayJson

@app.route('/submitMessage', methods=['POST'])
def submitMessage():
    #This is to submit a message.
    
    if not google_auth.is_logged_in():
        return flask.render_template('deny.html')
    
    message = request.form['message']
    fromDid = request.form['fromdid']
    targetDid = request.form['targetdid']
    
    
    if appdb.validateFrom(fromDid) == False:
        return json.dumps({'error': 'Unauthorized source phone number.'})
    
    #pprint.pprint('Got ' + message + ',' + fromDid)
    msg_id = appsms.sendsms(targetDid,fromDid,message)
    if msg_id == False: #This sends the sms!
        returndata = json.dumps({'error': 'Unable to send SMS'})
    else:
        msgTS = time.strftime("%Y-%m-%dT%H:%m:%SZ")
        appdb.logsms_db(msg_id, msgTS, 'outbound', targetDid, fromDid, 0.0040, 'pending', message)
        returndata = json.dumps({"msg" : message, "fromdid" : fromDid, 'targetdid' : targetDid,})
    return returndata

@app.route('/testAjax')
def testAjax():
    return json.dumps({"msg" : 'Success!'})

if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("8890")
    )
    
