#!/usr/bin/env python3
# This program runs a flask daemon to provide communications with flowroute n
#  stuff.
import time
# import datetime
import pprint
import configparser
import json
# import re
import flask


import appdb
import appsms
import app_settings
import app_auth
import callback_sms

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app", "debug")

app = flask.Flask(__name__)
app.secret_key = config.get("auth", "FN_FLASK_SECRET_KEY")

app.register_blueprint(callback_sms.app)
app.register_blueprint(app_settings.app)
app.register_blueprint(app_auth.app)

loginMsg = "You are not logged in."

if app_debug == '1':
    app.debug = True
else:
    app.debug = False


@app.route('/')
def index():
    '''This is the root index. If not logged in it displays homepage.html'''
    if flask.session.get('loginid'):
        user_info = appdb.getUserInfo(
            flask.session['email'], flask.session['loginid'])

        if not user_info:
            return flask.render_template('homepage.html', loggedin=False)

        rows = appdb.getDIDsbyAccount(flask.session['account_id'])
        return flask.render_template('index.html',
                                     name=user_info[2],
                                     picture=user_info[8],
                                     dids=rows,
                                     loggedin=True)
    else:
        return flask.render_template('homepage.html', loggedin=False)


@app.route('/landing')
def landingPage():
    '''This renders the landing page'''
    # user_info = google_auth.get_user_info()
    if flask.session['loginid']:
        user_info = appdb.getUserInfo(
            flask.session['email'], flask.session['loginid'])
    # Going to replace google_auth with a local authentication.
    if app_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    return flask.render_template(
        'landing.html', user_info=user_info, loggedin=loggedin)


@app.route('/single/<int:number>', methods=['GET'])
def manageSingleSMS(number):
    '''This renders a view for a single SMS number and its
    associated messages'''
    if not app_auth.is_logged_in():
        return flask.render_template(
            'deny.html', denymsg=loginMsg, loggedin=False)
    if flask.session['loginid']:
        user_info = appdb.getUserInfo(
            flask.session['email'], flask.session['loginid'])

    result = appdb.authIdforDID(user_info[0], number)
    prettynum = appsms.prettyPhone(number)

    if appdb.validateFrom(int(number)) and result:
        return flask.render_template(
            'single.html',
            srcnumber=number,
            prettynum=prettynum,
            loggedin=True)
    else:
        return flask.render_template(
            'notvalid.html',
            srcnumber=number,
            prettynum=prettynum,
            loggedin=True)

#Gotta redo this logic
@app.route('/getNumber/<int:number>',methods=['GET'])
def getNumMessages(number):
    '''Return the messages from a single DID in json form'''
    # This gets the mssages based on the provided from or two DID
    if not app_auth.is_logged_in():
        return json.dumps({'error': 'Unable to send SMS, you are not logged in'})

    # We need to take and compare the authIDforDID, gotta add use id
    # to getNumSMSLog and pull the id from result.
    userid = flask.session['account_id']
    result = appdb.authIdforDID(userid, number)
    smslog = appdb.getNumSMSLog(number, 10)

    i = 0
    msgjson = ""
    for line in smslog:
        prettyto = appsms.prettyPhone(line[7])
        prettyfrom = appsms.prettyPhone(line[6])
        if i >= 1:
            msgjson = msgjson + ',' + json.dumps({'to': prettyto,
                                                  'from': prettyfrom,
                                                  'body': line[9],
                                                  'timestamp': line[4],
                                                  'status': line[10]})
        else:
            msgjson = json.dumps({'to': prettyto,
                                  'from': prettyfrom,
                                  'body': line[9],
                                  'timestamp': line[4],
                                  'status': line[10]})
        i += 1
    msgArrayJson = '[' + msgjson + ']'
    return msgArrayJson


@app.route('/markread/<int:number>', methods=['GET'])
def markread(msg_id):
    '''This will mark the id for the message as read.'''
    if not app_auth.is_logged_in():
        return json.dumps({'error': 'Unable to send SMS, you are not logged in'})
    if appdb.updateReadStatus(msg_id, 1) == 0:
        return json.dumps({'error': 'Unable to update the read status.'})
    else:
        return json.dumps({'status': 'success'})


@app.route('/markallread', methods=['GET'])
def markallread():
    '''This will mark every EVERY I said, message for the user id which should
    be pulled from session info.'''
    if not app_auth.is_logged_in():
        return json.dumps({'error': 'Unable to send SMS, you are not logged in'})
    userid = flask.session['account_id']
    if appdb.updateMarkAllRead(userid) == 0:
        return json.dumps({'error':
                           'Nothing to update or error updating the read status.'})
    else:
        return json.dumps({'status': 'success'})
    return False


@app.route('/markallunread', methods=['GET'])
def markallunread():
    '''This will mark every EVERY I said, message for the user id which should
    be pulled from session info.'''
    if not app_auth.is_logged_in():
        return json.dumps({'error': 'Unable to send SMS, you are not logged in'})
    userid = flask.session['account_id']
    if appdb.updateMarkAllUnread(userid) == 0:
        return json.dumps({'error': 'Nothing to update or error updating the read status.'})
    else:
        return json.dumps({'status':'success'})
    return False


@app.route('/submitMessage', methods=['POST'])
def submitMessage():
    #This is to submit a message.

    if not app_auth.is_logged_in():
        return json.dumps({'error': 'Unable to send SMS'})

    message = flask.request.form['message']
    fromDid = flask.request.form['fromdid']
    targetDid = flask.request.form['targetdid']

    # user_info = appdb.getUserInfo(
    #                              flask.session['email'],
    #                              flask.session['loginid'])
    userid = flask.session['account_id']
    result = appdb.authIdforDID(userid, fromDid)

    if userid != result:
        return json.dumps({'error': 'Unauthorized UserID of ' + str(userid)
                           + " and DID id of " + str(result) + " and fromDID "
                           + str(fromDid)})

    if appdb.validateFrom(fromDid) is False:
        return json.dumps({'error': 'Unauthorized source phone number.'})

    uglyphone = appsms.uglyPhone(targetDid)

    # pprint.pprint('Got ' + message + ',' + fromDid)
    msg_id = appsms.sendsms(uglyphone, fromDid, message)
    if msg_id is False:  # This sends the sms!
        returndata = json.dumps({'error': 'Unable to send SMS'})
    else:
        msgTS = time.strftime("%Y-%m-%dT%H:%m:%S+00:00")
        appdb.logsms_db(msg_id, msgTS, 'outbound', uglyphone, fromDid,
                        0.0040, 'pending', message, result)
        returndata = json.dumps({"msg": message,
                                "fromdid": fromDid,
                                 "targetdid": targetDid})
    return returndata


@app.route('/testAjax')
def testAjax():
    return json.dumps({"msg": 'Success!'})


@app.route('/inbox')
def inbox():
    if app_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    return flask.render_template('inbox.html', loggedin=loggedin)


@app.route('/getInbox')
def returnInbox():
    if not app_auth.is_logged_in():
        return json.dumps({'error':
                           'Unable to send SMS, you are not logged in'})

    # userid = flask.session['account_id']
    loginId = flask.session['loginid']
    results = appdb.getSMSbyAccount(loginId, 20)
    # pprint.pprint(results)
    jsonresult = ''
    i = 0
    for x in results:
        if i >= 1:
            jsonresult += ',' + json.dumps({"msg": x[9],
                                            "fromdid": x[6],
                                            "targetdid": x[7]})
        else:
            jsonresult = json.dumps({"msg": x[9],
                                     "fromdid": x[6],
                                     "targetdid": x[7]})
        i += 1
    return jsonresult


@app.route('/launch')
def launchPage():
    if app_debug == '1':
        pprint.pprint(flask.session)
    if app_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False

    if app_debug == '1':
        pprint.pprint(loggedin)
        pprint.pprint("loggedin")

    return flask.render_template('launch.html', loggedin=loggedin)


@app.route('/pp')
def PrivacyPolicy():
    if app_debug == '1':
        pprint.pprint(flask.session)
    if app_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    return flask.render_template('pp.html', loggedin=loggedin)


@app.route('/tos')
def tos():
    if app_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    return flask.render_template('tos.html', loggedin=loggedin)


@app.route('/about')
def about():
    if app_auth.is_logged_in():
        loggedin = True
    else:
        loggedin = False
    return flask.render_template('about.html', loggedin=loggedin)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8890")
    )
