#!/usr/bin/env python3

import time
import datetime
import pprint
import configparser
import json
import appdb
from flask import Flask, render_template, request
app = Flask(__name__)
app.debug = True

config = configparser.ConfigParser()
config.read('config.ini')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submitMessage', methods=['POST'])
def submitMessage():
    message = request.form['message']
    fromDid = request.form['fromdid']
    targetDid = request.form['targetdid']
    
    pprint.pprint('Got ' + message + ',' + fromDid)
    
    if appdb.validateFrom(fromDid) == False:
        return json.dumps({'error': 'Unauthorized source'})
    
    returndata = json.dumps({"msg" : message, "fromdid" : fromDid, 'targetdid' : targetDid})
    return returndata

@app.route('/testAjax')
def testAjax():
    return json.dumps({"msg" : 'Success!'})

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8890")
    )
    