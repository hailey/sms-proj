#!/usr/bin/env python

import pprint
import os
import json
import random
import string
from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient

basic_auth_user_name = config.get("flowroute","fr_access_key")
basic_auth_password = config.get("flowroute","fr_secret_key")


mobile_number = os.environ.get('TO_NUMBER')
from_number = os.environ.get('FROM_NUMBER')

# Instantiate API client and create controllers for Messages
client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
messages_controller = client.messages

request_body = '{ \
  "data": { \
    "type": "message", \
    "attributes": { \
      "to": "' + str(mobile_number) + '", \
      "from": "' + str(from_number) + '", \
      "body": "Try me", \
      "is_mms": "false" \
    } \
  } \
}'

print ("---Send A Message")
result = messages_controller.send_a_message(request_body)
pprint.pprint(result)