#Python imports
import mysql.connector

#Project imports
from includes.config import *

def get_user(ID=None, login=None, nicename=None, email=None, displayname=None):
    db = mysql.connector.connect(**wpParams)
    c = db.cursor(dictionary=True)
    req = "SELECT * FROM wp_users "
    need_and=False
    req_tuple = ()
    if ID != None:
        req += " WHERE ID = %s"
        req_tuple=(ID,)
        need_and = True
    if login != None:
        if need_and:
            req +=" AND "
        else:
            req += " WHERE "
        req += " user_login = %s "
        req_tuple = req_tuple + (login,)
        need_and = True
    if nicename != None:
        if need_and:
            req +=" AND "
        else:
            req += " WHERE "
        req += " user_nicename = %s "
        req_tuple = req_tuple + (nicename,)
        need_and = True
    if email != None:
        if need_and:
            req +=" AND "
        else:
            req += " WHERE "
        req += " user_email = %s "
        req_tuple = req_tuple + (email,)
        need_and = True
    if displayname != None:
        if need_and:
            req +=" AND "
        else:
            req += " WHERE "
        req += " display_name = %s "
        req_tuple = req_tuple + (login,)
        need_and = True
    c.execute(req, req_tuple)
    users = c.fetchall()
    return users

def isTwined(academyA, academyB):
    db = mysql.connector.connect(**wpParams)
    c = db.cursor(dictionary=True)
    academies = (academyA, academyB, academyA, academyB)
    c.execute("SELECT * FROM wp_twinings WHERE academy_1 IN (%s,%s) AND academy_2 IN (%s,%s) AND academy_1 != academy_2 AND approved=1",academies)
    twining = c.fetchone()
    if twining == None:
        return False
    return True

def get_twining(a=None, b=None):
    db = mysql.connector.connect(**wpParams)
    c = db.cursor(dictionary=True)
    req = "SELECT * FROM wp_twinings "
    need_and=False
    req_tuple = ()
    if a != None:
        req += " WHERE academy_1 = %s"
        req_tuple=(a,)
        need_and = True
    if b != None:
        if need_and:
            req +=" AND "
        else:
            req += " WHERE "
        req += " academy_2 = %s "
        req_tuple = req_tuple + (b,)
        need_and = True
    c.execute(req, req_tuple)
    users = c.fetchall()
    return users

def get_twining_user(ID):
    if ID == None:
        return False
    db = mysql.connector.connect(**wpParams)
    c = db.cursor(dictionary=True)
    c.execute("SELECT * FROM wp_twinings WHERE academy_1 = %s OR academy_2 = %s",(ID, ID))
    twinings = c.fetchall()
    return twinings

def get_twining_user_complete(ID):
    db = mysql.connector.connect(**wpParams)
    c = db.cursor(dictionary=True)
    client = (ID, ID)
    c.execute("SELECT a1.user_login AS login,\
                    a1.user_email AS email,\
                    a1.ID AS academy_id,\
                    wp_twinings.ID AS twining_id\
            FROM wp_twinings\
            INNER JOIN wp_users a1 ON a1.ID = wp_twinings.academy_1\
            INNER JOIN wp_users a2 ON a2.ID = wp_twinings.academy_2\
            WHERE a2.ID =  %s\
            UNION ALL\
            SELECT a2.user_login AS login,\
                    a2.user_email AS email,\
                    a2.ID AS academy_id,\
                    wp_twinings.ID AS twining_id\
            FROM wp_twinings\
            INNER JOIN wp_users a1 ON a1.ID = wp_twinings.academy_1\
            INNER JOIN wp_users a2 ON a2.ID = wp_twinings.academy_2\
            WHERE a1.ID =  %s", client)
    twlist = c.fetchall()
    return twlist 

    



