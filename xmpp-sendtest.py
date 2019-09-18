#!/usr/bin/env python3
import configparser
import time
import MySQLdb

config = configparser.ConfigParser()
config.read('config.ini')

sqlhost = config.get("sql","sqlhost")
sqluser = config.get("sql","sqluser")
sqlpass = config.get("sql","sqlpass")
sqldb = config.get("sql","sqldb")
fraccesskey = config.get("flowroute","fr_access_key")
frsecretkey = config.get("flowroute","fr_secret_key")

phoneSource = config.get("phone","source")

