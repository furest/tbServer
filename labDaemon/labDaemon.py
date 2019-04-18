from config import *
import json
import socketserver
from threading import *
import mysql.connector
from methods import *
from listTwinings import *
import time
from makeAssociation import *
from sendMail import *
from pipeListener import *
from handleLabs import *


class labRequestHandler(socketserver.StreamRequestHandler):
    """
    Handles the requests.
    myself.request = socket to the client
    self.server = the server
    self.client_address = client's address
    self.rfile/self.wfile = file like socket
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
            #Checks that the message contains the ID of the incited academy
            if 'invited_id' not in dictData:
                errorRoutine(self.wfile, "No invited ID given")
                return
            initAcademy = retrieveAcademy(email=user['username'])
            twined = isTwined(initAcademy['ID'], dictData['invited_id'])
            if twined == False:
                errorRoutine(self.wfile, "This academy is not twined to the requested academy")
                return
            invitedLab = invitedLabs(user)
            if invitedLab != None:
                quitLab(user)
                deAssociate(invitedLab)
            lab = createLab(user)
            invitedAcademy = retrieveAcademy(id=dictData['invited_id'])
            sendPin(user['username'], invitedAcademy['user_email'],lab['pin']) 
            answerOK(self.wfile, lab)
        elif dictData['type'] == "join":
            if 'pin' not in dictData or dictData['pin'] == None :
                errorRoutine(self.wfile, "No pin given")
                return
            pin = dictData['pin']
            hostedLab = hostedLabs(user['ID'])
            if hostedLab != None:
                deleteLab(hostedLab)
                deAssociate(hostedLab)
            try:
                lab = joinLab(user['ID'], pin)
            except:
                errorRoutine(self.wfile, "User is already part of another lab!")
            if lab == None:
                errorRoutine(self.wfile, "Lab does not exist")
                return
            if lab == False:
                errorRoutine(self.wfile, "Lab already full")
                return
            print("Starting routing")
            if startRouting(lab) == False:
                print("routing failed!")
                errorRoutine(self.wfile, "An error occurred while establishing routing")
                stopRouting(lab)
                quitLab(user['ID'])
                return
            answerOK(self.wfile, {})
        else:
            errorRoutine("unknown request type")

if __name__ == "__main__":
    
    listener = PipeListener(config['PIPE'])
    listener.start()

    server = socketserver.ThreadingTCPServer((config['SRV_IP'], config['SRV_PORT']), labRequestHandler)
    print("Server created. Now serving")
    server.serve_forever()
