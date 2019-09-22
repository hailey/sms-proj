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
import appdb
import configparser
from flask import Flask, render_template, request
from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient
smsRate = 0.0040
fr_api_url = "https://api.flowroute.com/v2.1/messages"





########################
##      Code starts here
app = Flask(__name__)
app.debug = True

config = configparser.ConfigParser()
config.read('config.ini')
basic_auth_user_name = config.get("flowroute","fr_access_key")
basic_auth_password = config.get("flowroute","fr_secret_key")

client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
messages_controller = client.messages

#############################
##      Callback defs go here

@app.route('/sms-inbound', methods=['POST'])
def inboundsms():
    #extract attributes from POSTed JSON of inbound SMS
    json_content = request.json
    reply_to = json_content['data']['attributes']['from']
    reply_from = json_content['data']['attributes']['to']
    msg_id = json_content['data']['id']
    body = json_content['data']['attributes']['body']
    msg_timestamp = json_content['data']['attributes']['timestamp']
    
    msg_amount = re.search("\$?(\d.\d{1,5})",json_content['data']['attributes']['amount_display'])
    
    appdb.logsms_db(msg_id, msg_timestamp, 'inbound', reply_from, reply_to, msg_amount, body) # Lets log to our silly db.

    sendreply(reply_to, reply_from, "Message received. Please wait for a reply.")
    return "0"

def sendreply(reply_to, reply_from, msg):
    request_body = '{ \
  "data": { "type": "message", \
    "attributes": { \
      "to": "' + str(reply_to) + '", \
      "from": "' + str(reply_from) + '", \
      "body": "' + msg + '" \
    }   } }'

    result = messages_controller.send_a_message(request_body)
    if result:    
        msg_id = result['data']['id']
        appdb.logsms_db(msg_id, '', 'outbound', reply_to, reply_from, smsRate, msg) # Lets log to our silly db.
        return "0"
    return "-1"

#################
##      Main loop
if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8790")
    )