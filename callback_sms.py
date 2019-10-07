#!/usr/bin/env python3

import os
import urllib
import json
import pprint
import time
import datetime
import string
import appdb, appsms
import configparser
#from flask import Flask, render_template, request
import flask

########################
##      Code starts here
#app = Flask(__name__)
app = flask.Blueprint('callback-sms', __name__)
#app = flask.Flask(__name__)

#########
# This is so bare I don't need a config right now.
config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")

#############################
##      Callback defs go here
#@app.route('/')
#ef index():
#    return render_template('index.html')

def prettyStatus(status):
    if status == 'message buffered':
        return 'Delivered'
    elif status == 'smsc submit':
        return'Sent'
    elif status == 'smsc reject':
        return 'Rejected'
    elif status == 'delivery success':
        return 'Delivered'
    elif status == 'delivery failure':
        return 'Failed'
    elif status == 'smsc intermediate notifications':
        return 'Sent'

@app.route('/sms-inbound', methods=['POST'])
def smsinbound():
    #extract attributes from POSTed JSON of inbound SMS
    json_content = flask.request.json
    reply_to = json_content['data']['attributes']['from']
    reply_from = json_content['data']['attributes']['to']
    msg_id = json_content['data']['id']
    body = json_content['data']['attributes']['body']
    msg_timestamp = json_content['data']['attributes']['timestamp']
    smsRate = json_content['data']['attributes']['amount_display'].replace('$','')
    status = 'Delivered'
    account_id = appdb.getAccountbyDID(reply_from)
    appdb.logsms_db(msg_id, msg_timestamp, 'inbound', reply_from, reply_to, smsRate, status, body, account_id) # Lets log to our silly db.
    return "200"

@app.route('/dlr', methods=['POST','GET'])
def deliveryReport():
    #This is the delivery report callback function.
    json_content = flask.request.json
    pprint.pprint(json_content)
    msg_id = json_content['data']['id']
    msg_status = json_content['data']['attributes']['status']
    msg_timestamp = json_content['data']['attributes']['timestamp']
    pstatus = prettyStatus(msg_status)
    appdb.updateMsgStatus(msg_id, pstatus, msg_timestamp)
    return "0"