import json
import mysql.connector
from config import *
import random
def errorRoutine(writable, message):
    jsonError = { "error":True, "message":message}
    writable.write(json.dumps(jsonError).encode())

def retrieveUser(address):
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    ipClient = (address,)
    c.execute("SELECT * FROM CONNECTED_CLIENTS WHERE VIRT_IP = %s", ipClient)
    client = c.fetchone()
    return client

def generatePin(length):
    random.seed(a=None)#Uses system current time
    pin = random.randint(10**(length-1), int("9"*length))
    return pin

def answerOK(writer, obj):
    ans = {"error":False, "response":obj}
    strAns = json.dumps(ans) + "\n"
    writer.write(strAns.encode())

def retrieveAcademy(id = None, email = None):
    if id == None and email == None:
        return None
    db = mysql.connector.connect(**wpParams)
    c = db.cursor(dictionary=True)
    if id != None:
        c.execute("SELECT * FROM wp_users WHERE ID = %s", (id,))
    else:
        c.execute("SELECT * FROM wp_users WHERE user_email = %s", (email,))
    academy = c.fetchone()
    return academy

def isTwined(academyA, academyB):
    db = mysql.connector.connect(**wpParams)
    c = db.cursor(dictionary=True)
    academies = (academyA, academyB, academyA, academyB)
    c.execute("SELECT * FROM wp_twinings WHERE ACADEMY_1 IN (%s,%s) AND ACADEMY_2 IN (%s,%s) AND ACADEMY_1 != ACADEMY_2",academies)
    twining = c.fetchone()
    if twining == None:
        return False
    return True
