#!/usr/bin/python3

import mysql.connector
import crypt # used for crypt.crypt(pass, salt)
import os
import sys
from passlib.hash import phpass


log = open("/ovpn/wordpress.log", "a")
sys.stdout = log
def validateUser(username, password):
    q = "SELECT * FROM wp_users WHERE user_email = %s"
    usr = (username,)
    wpcursor.execute(q, usr)
    res = wpcursor.fetchone()
    if wpcursor.rowcount != 1:
        print("Error. %d rows fetched!" % wpcursor.rowcount)
        return False
    hashedpass = res['user_pass']
#    print("Hashed pass = %s" % hashedpass)
    if phpass.verify(secret=password.encode('utf-8'), hash=hashedpass):
    #if crypt.crypt(password, hashedpass) == password:
        print("login successful")
        return True
    else:
        print("Authentication failed!")
        return False 

wpdb = mysql.connector.connect(
    host="localhost",
    user="vpn",
    passwd="vpnpassword",
    database="wordpress"
)

wpcursor = wpdb.cursor(dictionary=True)
print(os.environ.get('username'))
print(os.environ.get('password'))
status = validateUser(os.environ.get('username'),os.environ.get('password'))
if status == True:
    print('OK')
    sys.exit(0)
else:
    print('FAIL')
    sys.exit(1)

    

