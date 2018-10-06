import os
import urllib
import requests
import json
import pprint
import time
from flask import Flask, request
from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

basic_auth_user_name = os.environ.get('FR_ACCESS_KEY')
basic_auth_password = os.environ.get('FR_SECRET_KEY')

from_number = os.environ.get('FROM_NUMBER')

client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
messages_controller = client.messages

#Flowroute API endpoint and reply SMS to be sent
fr_api_url = "https://api.flowroute.com/v2.1/messages"
reply_message = 'Thanks for the picture!'

app = Flask(__name__)
app.debug = True

@app.route('/inboundsms', methods=['POST'])
def inboundsms():

    #extract attributes from POSTed JSON of inbound MMS
    json_content = request.json
    reply_to = json_content['data']['attributes']['from']
    reply_from = json_content['data']['attributes']['to']
    body = json_content['data']['attributes']['body'].decode('utf-8')

    pprint.pprint(body)

    #send a reply SMS from your Flowroute number
    sendreply(reply_to, from_number, "You said " + body)
    file = open("sms-logs.txt","a") 
 
    file.write(reply_to +': ' + body + "\n") 
    file.close() 

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

    print ("---Send A Message")
    result = messages_controller.send_a_message(request_body)
    pprint.pprint(result)
    
    return '0'

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8090")
    )