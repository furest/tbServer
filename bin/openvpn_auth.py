#!/usr/bin/python3
#Python imports
import os, sys 
from passlib.hash import phpass

#Project imports
import includes.wordpress_access as wp

def authenticateUser(username, password):
    users = wp.get_user(email=username)
    if len(users) == 0:
        #User does not exist
        return False
    hashedpass = users[0]['user_pass']
    if phpass.verify(secret=password.encode('utf-8'), hash=hashedpass):
        #Authentication succeeded
        return True
    return False

if __name__ == "__main__":
    
    username = os.environ.get('username')
    password = os.environ.get('password')
    ret = authenticateUser(username, password)
    if ret == True:
        print("Authentication succeeded for user " + username)
        sys.exit(0)
    else:
        print("Authentication failed for user " + username)
        sys.exit(1)

