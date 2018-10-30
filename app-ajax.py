import time
import MySQLdb
import datetime
import pprint
import ConfigParser
from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)
app.debug = True

config = ConfigParser.ConfigParser()
config.read('config.ini')
sqlhost = config.get("sql","sqlhost")
sqluser = config.get("sql","sqluser")
sqlpass = config.get("sql","sqlpass")
sqldb = config.get("sql","sqldb")

############ Lets start our stuff
db = MySQLdb.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submitMessage', methods=['POST'])
def submitMessage():
    message = request.form['message']
    pprint.pprint('Got ' + message)
    return message

@app.route('/testAjax')
def testAjax():
    return 'Success'

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8090")
    )
    