#!/usr/bin/python3
import crypt
import spwd
import sys
import os
import time
def verify(username, password):
    try:
        enc_pwd = spwd.getspnam(username)[1]
        if enc_pwd in ["NP", "!", "", None]:
            return "user '%s' has no password set" % user
        if enc_pwd in ["LK", "*"]:
            return "account is locked"
        if enc_pwd == "!!":
            return "password has expired"
        if crypt.crypt(password, enc_pwd) == enc_pwd:
            return True
        else:
            return False
    except KeyError:
            return "user '%s' not found" % username
    return "unknown error"
print(os.environ.get('username'))
print(os.environ.get('password'))
time.sleep(120)
status = verify(os.environ.get('username'),os.environ.get('password'))
if status == True: 
    print('OK')
    sys.exit(0)
else:
    print('FAIL')
    sys.exit(1)

