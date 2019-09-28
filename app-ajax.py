#!/usr/bin/env python3

import time
import datetime
import pprint
import configparser
import json
import appdb, appsms
from flask import Flask, render_template, request
app = Flask(__name__)
app.debug = True

config = configparser.ConfigParser()
config.read('config.ini')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/single/<int:number>', methods=['GET'])
def manageSingleSMS(number):
    if appdb.validateFrom(int(number)):
        return render_template('single.html',srcnumber = number)
    else:
        return render_template('notvalid.html', srcnumber = number)

@app.route('/getMessages',methods=['GET'])
def getMessages():
    smslog = appdb.getAllSMSLog(10)
    #pprint.pprint(smslog)
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
    #This gets the mssages based on the provided from or two DID
    smslog = appdb.getNumSMSLog(did,10)
    #pprint.pprint(smslog)
    i = 0
    msgjson = ""
    for line in smslog:
        #pprint.pprint(line)
        if i >= 1:
            msgjson = msgjson + ',' + json.dumps({'to':line[7],
                              'from':line[6],
                              'body':line[9],
                              'timestamp': line[4]})
        else:
            msgjson =  json.dumps({'to':line[7],'from':line[6],'body':line[9],'timestamp': line[4]})
        i += 1
        
    
    msgArrayJson = '['+msgjson +']'
    return msgArrayJson

@app.route('/submitMessage', methods=['POST'])
def submitMessage():
    #This is to submit a message.
    message = request.form['message']
    fromDid = request.form['fromdid']
    targetDid = request.form['targetdid']
    
    if appdb.validateFrom(fromDid) == False:
        return json.dumps({'error': 'Unauthorized source phone number.'})
    
    pprint.pprint('Got ' + message + ',' + fromDid)
    msg_id = appsms.sendsms(targetDid,fromDid,message)
    if msg_id == False: #This sends the sms!
        returndata = json.dumps({'error': 'Unable to send SMS'})
    else:
        msgTS = time.strftime("%Y-%m-%dT%H:%m:%SZ")
        appdb.logsms_db(msg_id, msgTS, 'outbound', targetDid, fromDid, 0.0040, message)
        returndata = json.dumps({"msg" : message, "fromdid" : fromDid, 'targetdid' : targetDid,})
    return returndata

@app.route('/testAjax')
def testAjax():
    return json.dumps({"msg" : 'Success!'})

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8890")
    )
    