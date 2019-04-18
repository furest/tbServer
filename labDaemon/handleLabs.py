from config import *
import mysql.connector
from makeAssociation import *
from methods import *
import time

def createLab(user):
    v_ip = user["VIRT_IP"]
    userid = user["ID"]
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    pin = generatePin(config['PIN_LENGTH'])
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    newLab = (pin, user["ID"], now)
    inserted = False
    while not inserted:
        try:
            c.execute("INSERT INTO LABORATIONS(PIN, INIT_ACADEMY, STARTED_AT) VALUES (%s, %s, %s)", newLab)
        except mysql.connector.InterfaceError:
            pin = generatePin(config['PIN_LENGTH'])
            continue
        inserted = True
    db.commit()
    return {"id":c.lastrowid, "pin":pin}


def joinLab(user, pin):
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    newLab = (user, int(pin))
    c.execute("UPDATE LABORATIONS SET INVITED_ACADEMY = %s WHERE PIN = %s AND INVITED_ACADEMY IS NULL", newLab)
    #Check that a lab has actually been joined
    if c.rowcount == 0:
        return False
    db.commit()
    c.execute("SELECT acInit.ID as initID,\
                      acInit.VIRT_IP as initVIP,\
                      acInit.username as initUsername,\
                      acInvit.ID as invitID,\
                      acInvit.VIRT_IP as invitVIP,\
                      acInvit.username as initUsername,\
                      l.ID as labID,\
                      l.PIN as PIN \
                FROM LABORATIONS AS l \
                INNER JOIN CONNECTED_CLIENTS AS acInit ON l.INIT_ACADEMY = acInit.ID \
                INNER JOIN CONNECTED_CLIENTS AS acInvit ON l.INVITED_ACADEMY = acInvit.ID \
                WHERE PIN = %s", (int(pin),))
    lab = c.fetchone()
    return lab

def quitLab(user):
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    c.execute("UPDATE LABORATIONS SET INVITED_ACADEMY = NULL WHERE INVITED_ACADEMY = %s", (user,))
    c.commit()

def startRouting(lab):
     if associate(lab['initVIP'], lab['invitVIP']) == False:
         return False
     if associate(lab['invitVIP'], lab['initVIP']) == False:
         return False
     return True

def stopRouting(lab):
    deAssociate(lab['initVIP'], lab['invitVIP'])
    deAssociate(lab['invitVIP'], lab['initVIP'])

