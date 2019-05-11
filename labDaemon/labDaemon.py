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
import _thread

class labRequestHandler(socketserver.StreamRequestHandler):
    """
    Handles the requests.
    myself.request = socket to the client
    self.server = the server
    self.client_address = client's address
    self.rfile/self.wfile = file like socket
    """
    def log(self, message):
        print("[" + "]:",message)

    def errorRoutine(self, message):
        jsonError = { "error":True, "message":message}
        strError = json.dumps(jsonError) + "\n"
        self.log("Answered " + strError)
        self.wfile.write(strError.encode())

    def answerOK(self, obj):
        ans = {"error":False, "response":obj}
        self.log("Answered " + str(ans))
        strAns = json.dumps(ans) + "\n"
        self.wfile.write(strAns.encode())

    def handle(self):
        print(self.client_address)
        self.log("handling client" + str(self.client_address))
        #Reads the data sent by the client until the first \n
        stringData = self.rfile.readline().strip()
        self.log("received " + str(stringData))
        #Converting the json string to python dict
        try:
            dictData = json.loads(stringData)
        except:
            self.errorRoutine("Request is not in JSON format")
            return 
        if not "type" in dictData:
            self.errorRoutine("Request does not contain a type")
            return

        #Retrieves the email, REAL_IP, REAL_PORT of the requesting user
        user = retrieveUser(self.client_address[0])

        if(user == None):
            self.errorRoutine("IP is not bound to a user")
            return

        if dictData["type"] == "list":
            twiningsList = listTwinings(user["username"])
            self.log("list twinings:" + str(twiningsList))
            self.answerOK(twiningsList)
            return
        elif dictData["type"] == "create":
            #Checks that the message contains the ID of the incited academy
            if 'invited_id' not in dictData:
                self.errorRoutine("No invited ID given")
                return
            initAcademy = retrieveAcademy(email=user['username'])
            twined = isTwined(initAcademy['ID'], dictData['invited_id'])
            if twined == False:
                self.errorRoutine("This academy is not twined to the requested academy")
                return
            invitedLab = invitedLabs(user['ID'])
            if invitedLab != None:
                quitLab(user['ID'])
                delete_association(self.client_address[0])
            lab = createLab(user)
            invitedAcademy = retrieveAcademy(id=dictData['invited_id'])
            sendPin(user['username'], invitedAcademy['user_email'],lab['pin']) 
            self.answerOK(lab)
        elif dictData['type'] == "join":
            if 'pin' not in dictData or dictData['pin'] == None :
                self.errorRoutine("No pin given")
                return
            pin = dictData['pin']
            hostedLab = hostedLabs(user['ID'])
            if hostedLab != None:
                if pin == hostedLab['PIN']:
                    self.errorRoutine("You cannot join your own lab!")
                    return
                deleteLab(hostedLab)
                delete_association(self.client_address[0])
            try:
                lab = joinLab(user['ID'], pin)
            except:
                self.errorRoutine("User is already part of another lab!")
            if lab == None:
                self.errorRoutine("Lab does not exist")
                return
            if lab == False:
                self.errorRoutine("Lab already full")
                return
            self.log("Starting routing")
            if startRouting(lab) == False:
                self.log("routing failed!")
                self.errorRoutine("An error occurred while establishing routing")
                stopRouting(lab)
                quitLab(user['ID'])
                return
            self.answerOK({})
        elif dictData['type'] == "status":
            invited = None
            hosted = hostedLabs(user['ID'])
            if hosted == None:
                invited = invitedLabs(user['ID'])
                if invited != None:
                    fullLab = getLabDetails(invited['ID'])
                    self.answerOK({"status":"hosting", "lab":fullLab})
                    return
            else:
                fullLab = getLabDetails(hosted['ID'])
                self.answerOK({"status":"hosting", "lab":fullLab})
                return
            self.answerOK({"status":"free"})
            return
        else:
            self.errorRoutine("unknown request type")

if __name__ == "__main__":
    
    listener = PipeListener(config['PIPE'])
    listener.start()

    try:
        udpServer = socketserver.ThreadingTCPServer((config['UDP_SRV_IP'], config['UDP_SRV_PORT']), labRequestHandler)
        tcpServer = socketserver.ThreadingTCPServer((config['TCP_SRV_IP'], config['TCP_SRV_PORT']), labRequestHandler)
        _thread.start_new_thread(udpServer.serve_forever,())
        _thread.start_new_thread(tcpServer.serve_forever,())
        print("Server created. Now serving")
    except Exception as e:
        print(e)
        os._exit(1)
