from config import *
import json
import socketserver
from threading import *
import mysql.connector
from methods import *
from listTwinings import *
import time



def joinLab(user, pin):
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    newLab = (user, pin)
    c.execute("SELECT * FROM LABORATION WHERE PIN = %s", (pin,))
    lab = c.fetchone()
    if lab == None:
        return None
    if lab['INVITED_ACADEMY'] != None:
        return False
    lab['INVITED_ACADEMY']
    c.execute("UPDATE LABORATIONS SET INVITED_ACADEMY = %s WHERE PIN = %s AND INVITED_ACADEMY = NULL", newLab)
    #Check that a lab has actually been joined
    if c.rowcount == 0:
        return False
    return lab

def startRouting(lab):
    


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
        user = retrieveUser(self.client_address[0])

        if(user == None):
            errorRoutine(self.wfile, "IP is not bound to a user")
            return
        if dictData["type"] == "list":
            twiningsList = listTwinings(user["username"])
            print("list twinings:", twiningsList)
            answerOK(self.wfile,twiningsList)
            return
        elif dictData["type"] == "create":
            if 'invited_id' not in dictData:
                errorRoutine(self.wfile, "No invited ID given")
                return
            initAcademy = retrieveAcademy(email=user['username'])
            twined = isTwined(initAcademy['ID'], dictData['invited_id'])
            if twined == False:
                errorRoutine(self.wfile, "This academy is not twined to the requested academy")
                return
            lab = createLab(user)
            invitedAcademy = retrieveAcademy(id=dictData['invited_id'])
            sendPin(user['username'], invitedAcademy['user_email'],lab['pin']) 
            answerOK(self.wfile, lab)
        elif dictData['type'] == "join":
            if 'pin' not in dictData or dictData['pin'] == None or type(dictData['pin']) is not int:
                errorRoutine(self.wfile, "No pin given")
                return
            pin = dictData['pin']
            lab = joinLab(user['ID'], pin)
            if lab == None:
                errorRoutine(self.wfile, "Lab does not exist")
                return
            if ret == False:
                errorRoutine(self.wfile, "Lab already full")
                return
            startRouting(lab)

        else:
            errorRoutine("unknown request type")

if __name__ == "__main__":
    
    HOST, PORT = "172.16.100.1", 1500
    
    server = socketserver.ThreadingTCPServer((HOST, PORT), labRequestHandler)
    print("Server created. Now serving")
    server.serve_forever()
