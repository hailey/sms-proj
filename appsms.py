#!/usr/bin/env python3
# appsms.py
# import time
import re
import configparser
from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient

fr_api_url = "https://api.flowroute.com/v2.2/messages"

config = configparser.ConfigParser()
config.read('config.ini')
basic_auth_user_name = config.get("flowroute", "fr_access_key")
basic_auth_password = config.get("flowroute", "fr_secret_key")

client = FlowroutenumbersandmessagingClient(
    basic_auth_user_name, basic_auth_password)
messages_controller = client.messages


def prettyPhone(phonenumber):
    result = re.search(
        '1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})?',
        str(phonenumber))
    prettystr = "(" + result.group(1) + ") " +\
        result.group(2) + "-" + result.group(3)
    return prettystr


def uglyPhone(phonenumber):
    result = re.search(
        '1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})?',
        str(phonenumber))
    uglystr = "1" + result.group(1) + result.group(2) + result.group(3)
    return uglystr


def sendsms(reply_to, reply_from, msg):
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
        return msg_id
    return False
