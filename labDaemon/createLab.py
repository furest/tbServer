import mysql.connector
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
