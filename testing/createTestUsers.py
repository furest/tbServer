import os
import sys
import mysql.connector
from passlib.hash import phpass

USER="user"
PASSWORD="password"

def usage():
    print("Usage : " + sys.argv[0] + " [begin] end")


wpParams = {
    "host":"localhost",
    "user":"admin",
    "passwd":"AkyP3neGFaB689eK",
    "database":"wordpress"
}
tbParams = {
    "host":"localhost",
    "user":"admin",
    "passwd":"AkyP3neGFaB689eK",
    "database":"twinbridge"
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    begin = 0
    end = 0
    if len(sys.argv) == 2:
        end = int(sys.argv[1])
    else:
        begin = int(sys.argv[1])
        end=int(sys.argv[2])
    
    hasher = phpass.using(ident="P", rounds=13)
    user_ids = []
    for i in range(begin, end+1):
        wpdb = mysql.connector.connect(**wpParams)
        c = wpdb.cursor(dictionary=True)
        username = USER+str(i)
        hashedpass = hasher.hash(PASSWORD+str(i))
        email = "tb." + USER+str(i)+"@yopmail.com"
        c.execute("SELECT * FROM wp_users WHERE user_login = %s", (username,))
        dbuser = c.fetchone()
        if dbuser != None:
            c.execute("UPDATE wp_users SET user_pass=%s, user_email=%s WHERE ID=%s", (hashedpass, email, dbuser['ID']))
            user_ids.append(dbuser['ID'])
        else:
            c.execute("INSERT INTO wp_users(user_login, user_pass, user_email) VALUES (%s,%s,%s)", (username, hashedpass, email))
            user_ids.append(c.lastrowid)
        wpdb.commit()
    for i in range(begin, end, 2):
        tbdb = mysql.connector.connect(**tbParams)
        c = tbdb.cursor(dictionary=True)
        c.execute("INSERT INTO laborations(pin, init_academy, invited_academy) VALUES(%s,%s,%s)", ("test"+str(i), user_ids[i], user_ids[i+1]))
        tbdb.commit()







