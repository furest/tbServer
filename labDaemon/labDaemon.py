from config import *
import json
import socketserver
from threading import *
import mysql.connector
from methods import *
from listTwinings import *

wpParams = {
        "host": config['DB_WP_HOST']
        "user":config['DB_WP_USER'],
        "passwd":config['DB_WP_PASS'],
        "database":config['DB_WP_NAME']
    }
tbParams = {
        "host": config['DB_TB_HOST']
        "user":config['DB_TB_USER'],
        "passwd":config['DB_TB_PASS'],
        "database":config['DB_TB_NAME']
}

import random
import datetime

def generatePin(length):
    random.seed(a=None)#Uses system current time
    pin = random.randint(10**length, int("9"*length))
    return pin


def createLab(user, dbParams):
    v_ip = user["VIRT_IP"]
    userid = user["ID"]
    db = mysql.connector.connect(**dbParams)
    c = db.cursor(dictionnary=True)
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
    return {"id":c.lastrowid, "pin":pin}

def answerOK(writer, obj):
    ans = {"error":False, "response":obj}
    strAns = json.dumps(ans) + "\n"
    writer.write(strAns.encode())

def retrieveAcademy(academyId, dbParams):
    db = mysql.connector.connect(**dbParams)
    c = db.cursor(dictionary=True)
    c.execute("SELECT * FROM wp_users WHERE ID = %s", (academyId,))
    academy = c.fetchone()
    return academy

def isTwined(academyA, academyB, dbParams):
    db = mysql.connector.connect(**dbParams)
    c = db.cursor(dictionary=True)
    academies = (academyA, academyB, academyA, academyB)
    c.execute("SELECT * FROM wp_twinings WHERE ACADEMY_1 IN (%s,%s) AND ACADEMY_2 IN (%s,%s) AND ACADEMY_1 != ACADEMY_2",academies)
    twining = c.fetchone()
    if twining == None:
        return False
    return True

class labRequestHandler(socketserver.StreamRequestHandler):
    """
    Handles the requests.
    myself.request = socket to the client
    self.server = the server
    self.client_address = client's address
    self.rfile/self.wfile = file like 
    """

    def handle(self):
        print("handling client",self.client_address)
        #Reads the data sent by the client until the first \n
        stringData = self.rfile.readline().strip()
        print("received ", stringData)
        #Converting the json string to python dict
        try:
            dictData = json.loads(stringData)
        except:
            errorRoutine(self.wfile, "Request is not in JSON format")
            return 
        if not "type" in dictData:
            errorRoutine(self.wfile, "Request does not contain a type")
            return

        #Retrieves the email, REAL_IP, REAL_PORT of the requesting user
        user = retrieveUser(tbParams, self.client_address[0])

        if(user == None):
            errorRoutine(self.wfile, "IP is not bound to a user")
            return
        if dictData["type"] == "list":
            twiningsList = listTwinings(user["username"], wpParams)
            print("list twinings:", twiningsList)
            answerOK(self.wfile,twiningsList)
            return
        elif dictData["type"] == "create":
            if 'invited_id' not in dictData:
                errorRoutine(self.wfile, "No invited ID given")
                return
            lab = createLab(user)
            isTwined = checkTwining(user['id'], invitedAcademy,wpParams)
            invitedAcademy = retrieveAcademy(dictData['invited_id'],wpParams)
            answerOK(self.wfile, lab)
                    
        else:
            errorRoutine("unknown request type")

if __name__ == "__main__":
    
    HOST, PORT = "172.16.100.1", 1500
    
    server = socketserver.ThreadingTCPServer((HOST, PORT), labRequestHandler)
    print("Server created. Now serving")
    server.serve_forever()
