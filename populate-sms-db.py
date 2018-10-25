#make sms db.
import sqlite3

smsdb = sqlite3.connect('sms.db')
smscursor = smsdb.cursor()

smscursor.execute('''CREATE TABLE sms
             (id text, date text, to_did text, from_did text, message text)''')

smscursor.execute("INSERT INTO sms VALUES ('0','2006-01-05 01:49:10','9515551212','4245556053','booooooooooooooo')")
smscursor.execute("INSERT INTO sms VALUES ('1','2006-01-05 01:49:14','9515551212','4245556053','hihi hows you?')")


# Save (commit) the changes
smsdb.commit()