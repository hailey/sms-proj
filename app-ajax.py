import time
import datetime
import pprint
import ConfigParser
import json
import appdb
from flask import Flask, render_template, request
app = Flask(__name__)
app.debug = True

config = ConfigParser.ConfigParser()
config.read('config.ini')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submitMessage', methods=['POST'])
def submitMessage():
    message = request.form['message']
    fromDid = request.form['fromdid']
    pprint.pprint('Got ' + message + ',' + fromDid)
    
    if appdb.validateFrom(fromDid) == False:
        return "Not Authed"
    returndata = json.dumps({"msg" : message, "fromdid" : fromDid})
    return returndata

@app.route('/testAjax')
def testAjax():
    return 'Success'

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8090")
    )
    