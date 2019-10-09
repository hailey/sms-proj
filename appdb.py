#!/usr/bin/env python3
#appdb.py
#We connect to our database and any database calls are put into functions here.

import pymysql
import pymysql.cursors
import pprint
#import time
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
sqlhost = config.get("sql","sqlhost")
sqluser = config.get("sql","sqluser")
sqlpass = config.get("sql","sqlpass")
sqldb = config.get("sql","sqldb")


def logsms_db(msg_id, msg_ts, direction, to_did, from_did, cost, status, msg, account_id):
    #This statement logs a SMS to the smslog table.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()

    cur.execute("INSERT INTO messages (`timestamp`, `provider_timestamp`,`direction`, `source_number`, `dest_number`, `cost`,`pid`,`status`, `body`, `account_id`)VALUES \
                (now(), %s, %s, %s, %s, %s, %s, %s, %s, %s)",(msg_ts, direction, from_did, to_did, cost, msg_id, status, msg, account_id))
    db.commit()
    db.close()
    return True

def isUserinDB(google_id):
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT * FROM account WHERE google_id=%s LIMIT 1" % google_id)
    data = cur.fetchone()
    db.close()
    if data:
        pprint.pprint(data)
        return True
    else:
        return False
    
def isUserVerfied(google_id):
    #This checks to see if the account is set to verified true
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT verified_email FROM account WHERE google_id=%s",(google_id))
    data = cur.fetchone()
    db.close()
    if data:
        pprint.pprint(data)
        return True
    else:
        return False

def setNewUser(google_id, refresh_token, name, email, verified):
    #This statement is for creating a user into the account table.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("INSERT INTO account (`name`, `email`, `refresh_token`, `google_id`, `verified_email`, `created`, `last_modified`) VALUES \
                (%s, %s, %s, %s, %s, NOW(), NOW())",(name, email, refresh_token, google_id, verified))
    db.commit()
    db.close()
    return True

def getInfobyEmail(email):
    #This pulls * from 'account' and returns it if it matches an email.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT * FROM account WHERE email=%s LIMIT 1",(email))
    data = cur.fetchone()
    db.close()
    if not data:
        return False
    return data

def getUserIdFromRT(refreshtoken):
    #This pulls an UserID from a Refresh Token
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT id FROM account WHERE refresh_token=%s",(refreshtoken))
    data = cur.fetchone()
    db.close()
    if not data:
        return False
    return data[0]

def getUserIDfromGoogleID(google_id):
    #This pulls an UserID from a Google ID
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT id FROM account WHERE google_id=%s",(google_id))
    data = cur.fetchone()
    db.close()
    if not data:
        return False
    return data[0]

def getAccountbyDID(did):
    #This function pulls the account id for the DID in the query.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT account_id FROM dids WHERE number=%s LIMIT 1",(did))
    data = cur.fetchone()
    db.close()
    if not data:
        return False
    return data[0]

def getDIDsbyAccount(account_id):
    #DIDs that are assigned to an account.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT number,provider FROM dids WHERE account_id=%s",(account_id))
    rows = cur.fetchall()
    db.close()
    return rows 
    

def authIdforDID(account_id,did):
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT account.id FROM dids,account WHERE dids.account_id=account.id AND account.id=%s AND dids.number=%s LIMIT 1",(account_id,did))
    data = cur.fetchone()
    db.close()
    if data:
    #pprint.pprint('-----')
    #pprint.pprint(data)
    #pprint.pprint('----')
        return data[0]
    else:
        return False

def setRefreshToken(refresh_token, google_id):
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    pprint.pprint("Setting new refresh token of " + google_id + " and " + refresh_token)
    cur.execute("UPDATE account SET refresh_token=%s WHERE google_id=%s",(refresh_token, google_id))
    db.commit()
    db.close()
    return True

def getAllSMSLog(limit=5, order='desc'):
    #This gets the last X amount of logs from all numbers.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT %s",(limit))
    rows = cur.fetchall()
    db.close()
    return rows

def getNumSMSLog(did, limit=5):
    #This gets the last X amount of logs from all numbers.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT * FROM messages WHERE source_number=%s OR dest_number=%s ORDER BY timestamp DESC LIMIT %s",(did,did,limit))
    rows = cur.fetchall()
    #for row in rows:
        #pprint.pprint(row)
    db.close()
    return rows
    
def updateMsgStatus(msg_id, status, msg_timestamp):
    #Update the delivered field in the database based on delivery reports.
    #UPDATE messages SET delivered='success' WHERE pid='mdr2-46999f9ce19e11e99074722a1f1f4bb4'
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    affected_count = cur.execute("UPDATE `messages` SET status=%s, `provider_timestamp`=%s WHERE `pid`=%s",(status, msg_timestamp ,msg_id))
    db.commit()
    db.close()
    return True

def updateMsgTimestamp(msg_id, timestamp):
    #This changes the timestamp of the msg_id to the timestamp provided by the provider.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    affected_count = cur.execute("UPDATE `messages` SET `provider_timestamp`=%s WHERE `pid`=%s",(timestamp,msg_id))
    db.commit()
    db.close()

# We gotta do lookups or checks here.. prolly a database call, but right now its an if statement.
def validateFrom(did):
    #this statement is here for testing. It bypasses DBs.
    if '17605551212' == did: 
        return True
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT number FROM dids WHERE number=%s LIMIT 1" % did)
    data = cur.fetchone()
    db.close()
    if data != None and int(data[0]) == int(did):
        return True    
    return False
