import os
import urllib
import requests
import json
import pprint
import time
import sqlite3
import datetime
from flask import Flask, request
from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

counter = 1

basic_auth_user_name = os.environ.get('FR_ACCESS_KEY')
basic_auth_password = os.environ.get('FR_SECRET_KEY')
from_number = os.environ.get('FROM_NUMBER')


client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
messages_controller = client.messages

#Flowroute API endpoint and reply SMS to be sent
fr_api_url = "https://api.flowroute.com/v2.1/messages"

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
    body = json_content['data']['attributes']['body'].decode('utf-8')

    pprint.pprint(body)
    if body.lower() == u'count'.lower():
        sendreply(reply_to, reply_from, "There have been " + str(counter) + " messages sent to this system.")
    elif body.lower() == u'help'.lower():
        sendreply(reply_to, reply_from, "Right now only the command 'count' works.")
    else:       #Echo a reply
        sendreply(reply_to, reply_from, "What? You should type 'help' for a list of valid commands")
    
    logsqlite(msg_id, reply_from, reply_to, body) # Lets log to our silly db.

    counter += 1
    return '0'

@app.route('/smscount', methods=['GET'])
def smscount():
    print("Returning the count of " + str(counter) + ".")
    return str(counter)

def logsqlite(msg_id, to_did, from_did, msg):
    smsdb = sqlite3.connect('sms.db')
    smscursor = smsdb.cursor()
    smscursor.execute("INSERT INTO sms VALUES (?,?,?,?,?)", (msg_id,datetime.datetime.now(),to_did, from_did, msg))
    smsdb.commit()
    smsdb.close()
    return '0'

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
    #pprint.pprint(result)    
    return '0'

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8090")
    )