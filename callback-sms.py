#!/usr/bin/env python3

import os
import urllib
import json
import pprint
import time
import datetime
import sys
import string
import re
import io
import appdb, appsms
import configparser
from flask import Flask, render_template, request


########################
##      Code starts here
app = Flask(__name__)

#########
# This is so bare I don't need a config right now.
config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")

#############################
##      Callback defs go here
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sms-inbound', methods=['POST'])
def smsinbound():
    #extract attributes from POSTed JSON of inbound SMS
    json_content = request.json
    reply_to = json_content['data']['attributes']['from']
    reply_from = json_content['data']['attributes']['to']
    msg_id = json_content['data']['id']
    body = json_content['data']['attributes']['body']
    msg_timestamp = json_content['data']['attributes']['timestamp']
    smsRate = json_content['data']['attributes']['amount_display'].replace('$','')
    status = 'success'

    appdb.logsms_db(msg_id, msg_timestamp, 'inbound', reply_from, reply_to, smsRate, status, body) # Lets log to our silly db.
    #This command seems to make this function happen twice.
#    appsms.sendsms(reply_to, reply_from, "Message received. Please wait for a reply.")
    return "0"

@app.route('/dlr', methods=['POST','GET'])
def deliveryReport():
    json_content = request.json
    pprint.pprint(json_content)
    msg_id = json_content['data']['id']
    msg_status = json_content['data']['attributes']['status']
    msg_timestamp = json_content['data']['attributes']['timestamp']
    appdb.updateMsgStatus(msg_id, msg_status, msg_timestamp)
    return "0"

#################
##      Main loop
if __name__ == '__main__':
    if app_debug == '1':
        app.debug = True
    else:
        app.debug = False
    app.run(
        host="0.0.0.0",
        port=8790
    )
