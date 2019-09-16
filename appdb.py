#appdb.py
#We connect to our database and any database calls are put into functions here.

import MySQLdb
import time
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('config.ini')
sqlhost = config.get("sql","sqlhost")
sqluser = config.get("sql","sqluser")
sqlpass = config.get("sql","sqlpass")
sqldb = config.get("sql","sqldb")


db = MySQLdb.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)

def logsms_db(msg_id, msg_ts, direction, to_did, from_did, cost, msg):
    db.ping()
    cur = db.cursor()
    cur.execute("INSERT INTO messages (`timestamp`, `provider_timestamp`,`direction`, `source_number`, `dest_number`, `cost`,`pid`, `body`)VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s)",(int(time.time()),msg_ts, direction, from_did, to_did, cost, msg_id, msg))
    db.commit()
    return True

# We gotta do lookups or checks here.. prolly a database call, but right now its an if statement.
def validateFrom(did):
    #this statement is here for testing. It bypasses DBs.
    if '17605551212' == did: 
        return True
    db.ping()
    cursor = db.cursor()
    cursor.execute("SELECT number FROM dids WHERE number=%s LIMIT 1" % did)
    data = cursor.fetchone()
    if data != None and data[0] == did:
        return True    
    return False