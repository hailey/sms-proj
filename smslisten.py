#!/usr/bin/env python3

import os
import urllib
#import requests
import json
import pprint
import time
import MySQLdb
import datetime
import configparser
from flask import Flask, request
from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient

import sys

counter = 1
config = configparser.ConfigParser()
config.read('config.ini')
sqlhost = config.get("sql","sqlhost")
sqluser = config.get("sql","sqluser")
sqlpass = config.get("sql","sqlpass")
sqldb = config.get("sql","sqldb")

smsRate = 0.0040

basic_auth_user_name = config.get("flowroute","fr_access_key")
basic_auth_password = config.get("flowroute","fr_secret_key")

client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
messages_controller = client.messages

#Flowroute API endpoint and reply SMS to be sent
fr_api_url = "https://api.flowroute.com/v2.1/messages"

############ Lets start our stuff
db = MySQLdb.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)

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
    
    logmysql(msg_id, json_content['data']['attributes']['timestamp'], 'inbound', reply_from, reply_to,json_content['data']['attributes']['amount_display'], body) # Lets log to our silly db.
    
    pprint.pprint(body)
    pprint.pprint(reply_from)
    pprint.pprint(reply_to)
    if body.lower() == u'count'.lower():
        print('Sending count reply.')
        sendreply(reply_to, reply_from, "There have been " + str(counter) + " messages sent to this system.")
    elif body.lower() == u'help'.lower():
        print('Sending help reply.')
        sendreply(reply_to, reply_from, "Right now only the command 'count' works.")
    else:       #Echo a reply
        sendreply(reply_to, reply_from, "What? You should type 'help' for a list of valid commands")

    counter += 1
    return '0'

@app.route('/smscount', methods=['GET'])
def smscount():
    print("Returning the count of " + str(counter) + ".")
    return str(counter)

def logmysql(msg_id, msg_ts, direction, to_did, from_did, cost, msg):
    cur = db.cursor()
    cur.execute("INSERT INTO messages (`timestamp`, `provider_timestamp`,`direction`, `source_number`, `dest_number`, `cost`,`pid`, `body`)VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s)",(int(time.time()),msg_ts, direction, from_did, to_did, cost, msg_id, msg))
    db.commit()
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
    pprint.pprint(result)
   
    msg_id = result['data']['id']
    logmysql(msg_id, '', 'outbound', reply_to, reply_from,smsRate, msg) # Lets log to our silly db.

    print ("ID: ", msg_id)
    return '0'

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8790")
    )