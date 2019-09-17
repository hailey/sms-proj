#!/usr/bin/env python3
# Populate mariadb/mysqldb !
# Okay so lets do this right.

import MySQLdb
import configparser
import time

config = configparser.ConfigParser()
config.read('config.ini')

sqlhost = config.get("sql","sqlhost")
sqluser = config.get("sql","sqluser")
sqlpass = config.get("sql","sqlpass")
sqldb = config.get("sql","sqldb")


db = MySQLdb.connect(host=sqlhost, user=sqluser, passwd=sqlpass, db=sqldb)

cur = db.cursor()
 
# Select data from table using SQL query.
cur.execute("INSERT INTO messages (`timestamp`, `provider_timestamp`, `source_number`, `dest_number`, `cost`, `body`)VALUES(%s, %s, %s, %s, %s, %s)",(int(time.time()),'2017-01-12 12:12:32Z','7505551212','8185551212','0.0040','hi there baby how are you?'))
db.commit()
cur.execute("SELECT * FROM messages")
 
# print the first and second columns      
for row in cur.fetchall() :
    print (row[1], " ", row[2])
