#!/usr/bin/env python3
#appdb.py
#We connect to our database and any database calls are put into functions here.

import pymysql
import pymysql.cursors
import pprint
import time
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
sqlhost = config.get("sql","sqlhost")
sqluser = config.get("sql","sqluser")
sqlpass = config.get("sql","sqlpass")
sqldb = config.get("sql","sqldb")


def logsms_db(msg_id, msg_ts, direction, to_did, from_did, cost, msg):
    #This statement logs a SMS to the smslog table.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("INSERT INTO messages (`timestamp`, `provider_timestamp`,`direction`, `source_number`, `dest_number`, `cost`,`pid`, `body`)VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s)",(int(time.time()),msg_ts, direction, from_did, to_did, cost, msg_id, msg))
    db.commit()
    db.close()
    return True

def getAllSMSLog(limit=5,order='desc'):
    #This gets the last X amount of logs from all numbers.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT %s;",(limit))
    rows = cur.fetchall()
    #for row in rows:
        #pprint.pprint(row)
    db.close()
    return rows

def getNumSMSLog(did,limit=5):
    #This gets the last X amount of logs from all numbers.
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT * FROM messages WHERE source_number=%s OR dest_number=%s ORDER BY timestamp DESC LIMIT %s",(did,did,limit))
    rows = cur.fetchall()
    #for row in rows:
        #pprint.pprint(row)
    db.close()
    return rows
    
def updateMsgStatus(msg_id,status, msg_timestamp):
    #Update the delivered field in the database based on delivery reports.
    #UPDATE messages SET delivered='success' WHERE pid='mdr2-46999f9ce19e11e99074722a1f1f4bb4'
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    affected_count = cur.execute("UPDATE `messages` SET status=%s, `provider_timestamp`=%s WHERE `pid`=%s",(status, msg_timestamp ,msg_id))
    db.commit()
    db.close()
    return True

def updateMsgTimestamp(msg_id,timestamp):
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
        return Trueh
    db = pymysql.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)
    cur = db.cursor()
    cur.execute("SELECT number FROM dids WHERE number=%s LIMIT 1" % did)
    data = cur.fetchone()
    db.close()
    if data != None and int(data[0]) == int(did):
        return True    
    return False
