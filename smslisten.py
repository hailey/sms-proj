#!/usr/bin/env python3

import os
import urllib
import appdb
import json
import pprint
import time
#import PyMySQL
import datetime

import configparser
from flask import Flask, request
from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient

import sys

counter = 1
config = configparser.ConfigParser()
config.read('config.ini')

smsRate = 0.0040

basic_auth_user_name = config.get("flowroute","fr_access_key")
basic_auth_password = config.get("flowroute","fr_secret_key")

client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
messages_controller = client.messages

#Flowroute API endpoint and reply SMS to be sent
fr_api_url = "https://api.flowroute.com/v2.2/messages"

############ Lets start our stuff

app = Flask(__name__)
app.debug = True

@app.route('/inboundsms', methods=['POST'])
def inboundsms():
    global counter
    #extract attributes from POSTed JSON of inbound SMS
    json_content = request.json
    reply_to = json_content['data']['attributes']['from']
    reply_from = json_content['data']['attributes']['to']
    msg_id = json_content['data']['id']
    body = json_content['data']['attributes']['body']
    
    appdb.logsms_db(msg_id, json_content['data']['attributes']['timestamp'], 'inbound', reply_from, reply_to,json_content['data']['attributes']['amount_display'], body) # Lets log to our silly db.
    
    pprint.pprint(body)
    if body.lower() == u'count'.lower():
        print('Sending count reply.')
        smsMessage =  "There have been " + str(counter) + " messages sent to this system."
    elif body.lower() == u'help'.lower():
        print('Sending help reply.')
        smsMessage = "Right now only the command 'count' works."
    else:       #Echo a reply
        smsMessage = "What? You should type 'help' for a list of valid commands"
    sendreply(reply_to, reply_from, smsMessage)
    counter += 1
    return 'Success'

@app.route('/smscount', methods=['GET'])
def smscount():
    print("Returning the count of " + str(counter) + ".")
    return str(counter)

def sendreply(reply_to, reply_from, msg):
    request_body = '{ \
  "data": { \
    "type": "message", \
    "attributes": { \
      "to": "' + str(reply_to) + '", \
      "from": "' + str(reply_from) + '", \
      "body": "' + msg + '", \
      "is_mms": "false" \
    } \
  } \
}'

    print ("---Returning message")
    result = messages_controller.send_a_message(request_body)
    pprint.pprint(result)
   
    msg_id = result['data']['id']
    appdb.logsms_db(msg_id, '', 'outbound', reply_to, reply_from,smsRate, msg) # Lets log to our silly db.

    print ("ID: ", msg_id)
    return '0'

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8790")
    )