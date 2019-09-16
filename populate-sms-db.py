#make sms db.
import sqlite3

smsdb = sqlite3.connect('sms.db')
smscursor = smsdb.cursor()

smscursor.execute('''CREATE TABLE sms
             (id text, date int, to_did text, from_did text, message text)''')

smscursor.execute("INSERT INTO sms VALUES ('0','1416668938','9515551212','4245556053','booooooooooooooo')")
smscursor.execute("INSERT INTO sms VALUES ('1','1416668939','9515551212','4245556053','hihi hows you?')")


# Save (commit) the changes
smsdb.commit()