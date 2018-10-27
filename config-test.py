# config-test.py
# This file will run and tell you the values of the configuration.

import ConfigParser
config = ConfigParser.ConfigParser()
config.read('config.ini')

sqlhost = config.get("sql","sqlhost")
sqluser = config.get("sql","sqluser")
sqlpass = config.get("sql","sqlpass")
sqldb = config.get("sql","sqldb")
fraccesskey = config.get("flowroute","fr_access_key")
frsecretkey = config.get("flowroute","fr_secret_key")

print("You got the following settings...\n")
print ("Host: " + sqlhost)
print ("User: " + sqluser)
print ("Pass: " + sqlpass)
print ("Database: " + sqldb)

print ("Flowroute info:")
print ("Access Key: " + fraccesskey)
print ("Secret Key: " + frsecretkey)