#Python imports
import json
import socketserver
from threading import *
import mysql.connector
import time
import _thread

#Project imports
from includes.config import *
from includes.methods import *
from includes.makeAssociation import *
from includes.sendMail import *
from includes.pipeListener import *
import includes.wordpress_access as wp
import includes.twinbridge_access as tb
from includes.labCleaner import *
from includes.labAnalyser import *
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
        jsonError = { "error":True, "reason":message}
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

        #Retrieves the tuple of the current user
        user = tb.get_connected_client(virt_ip=self.client_address[0])


        if(len(user) == 0):
            self.errorRoutine("IP is not bound to a user")
            return
        user = user[0]

        if dictData["type"] == "list":
            twiningsList = wp.get_twining_user_complete(user['ID'])
            self.log("list twinings:" + str(twiningsList))
            self.answerOK(twiningsList)
            return
        elif dictData["type"] == "create":
            #Checks that the message contains the ID of the invited academy
            if 'invited_id' not in dictData:
                self.errorRoutine("No invited ID given")
                return
            twined = wp.isTwined(user['ID'], dictData['invited_id'])
            if twined == False:
                self.errorRoutine("This academy is not twined to the requested academy")
                return

            #Check if client is already invited in another lab
            invitedLabs = tb.get_lab(invited_academy=user['ID'], over=False)
            if len(invitedLabs) != 0:
                self.errorRoutine("This academy is currently invited in another lab")
                return
                #Removes client from the old lab
                #tb.update_labs(ID=invitedLabs[0]['ID'], invited_academy=None)
                #Stop the routing
                #delete_association(self.client_address[0])

            #Check if the client already hosts a lab
            hostedLabs = tb.get_lab(init_academy=user['ID'], over=False)
            lab = None
            if len(hostedLabs) == 0:
                #Lab needs to be created first
                created=False
                inserted_id = None
                while not created:
                    try:
                        inserted_id = tb.insert_lab(init_academy=user['ID'], pin=generatePin(config['PIN_LENGTH']))
                    except mysql.connector.errors.IntegrityError as err:
                        if "pin" in err.msg:
                            inserted_id=None
                            continue
                        else:
                            inserted_id=None
                            self.errorRoutine("An error occurred while creating the lab")
                            self.log("Error while creating : " + err.msg)
                            return
                    created=True
                lab = tb.get_lab(ID=inserted_id)
                lab = lab[0]
            else:
                lab = hostedLabs[0]
            init_user = wp.get_user(ID=user['ID'])
            invited_user = wp.get_user(ID=dictData['invited_id'])
            sendPin(init_user[0]['user_nicename'], invited_user[0]['user_email'], lab['pin'])
            del lab['started_at']
            self.answerOK(lab)
            return
        elif dictData['type'] == "join":
            if 'pin' not in dictData or dictData['pin'] == None or dictData['pin'] == "":
                self.errorRoutine("No pin given")
                return
            pin = dictData['pin']
            
            #Check if the user already host a lab
            hostedLabs = tb.get_lab(init_academy=user['ID'], over=False)
            if len(hostedLabs) != 0:
                #If the target lab is the hosted lab then return an error
                if pin == hostedLabs[0]['pin']:
                    self.errorRoutine("You cannot join your own lab!")
                    return
                self.errorRoutine("This academy already host a lab")
                return
                #
                #Otherwise delete the old lab
                #tb.delete_lab(ID=hostedLabs[0]['ID'])
                #delete_association(self.client_address[0])
            invitedLabs = tb.get_lab(invited_academy=user['ID'], over=False)
            if len(invitedLabs) != 0:
                self.errorRoutine("This academy is already invited in another lab")
                return

            requested_lab = tb.get_lab(pin=pin, over=False)

            if len(requested_lab) == 0:
                self.errorRoutine("Lab does not exist")
                return
            if requested_lab[0]['invited_academy'] != None:
                self.errorRoutine("Lab already full")
                return
            tb.update_labs(ID=requested_lab[0]['ID'], invited_academy=user['ID'])
            self.log("Starting routing")
            invited_virt_ip = user['virt_ip']

            #Check if both clients are connected
            init_client = tb.get_connected_client(ID=requested_lab[0]['init_academy'])
            if len(init_client) != 0:
                #Both clients are connected. Start routing. Otherwise OpenVPN will do it upon connexion
                if associate(invited_virt_ip, init_client[0]['virt_ip']) == False:
                    delete_association(invited_virt_ip)
                    self.log("Error while establishing routing between " + invited_virt_ip + " and " + init_client[0]['virt_ip'])
                    self.errorRoutine("An error occurred while establishing routing")
                    return
                self.answerOK({})
        elif dictData['type'] == "status":
            invited = None
            hosted_labs = tb.get_lab(init_academy=user['ID'], over=False)
            if len(hosted_labs) == 0:
                invited_labs = tb.get_lab(invited_academy=user['ID'], over=False)
                if len(invited_labs) != 0:
                    fullLab = getLabDetails(invited_labs[0]['ID'])
                    if fullLab['invit_id'] != None:
                        invited_user = wp.get_user(fullLab['invit_id'])
                        fullLab['invit_username'] = invited_user[0]['user_nicename']
                    if fullLab['init_id'] != None:
                        init_user = wp.get_user(fullLab['init_id'])
                        fullLab['init_username'] = init_user[0]['user_nicename']
                    self.answerOK({"status":"invited", "lab":fullLab})
                    return
            else:
                #return an array with lab_id, lab_pin, lab_starttime, init_id, init_username, init_ip, invit_id, invit_username, invit_ip
                fullLab = getLabDetails(hosted_labs[0]['ID'])
                if fullLab['invit_id'] != None:
                    invited_user = wp.get_user(fullLab['invit_id'])
                    fullLab['invit_username'] = invited_user[0]['user_nicename']
                if fullLab['init_id'] != None:
                    init_user = wp.get_user(fullLab['init_id'])
                    fullLab['init_username'] = init_user[0]['user_nicename']
                self.answerOK({"status":"hosting", "lab":fullLab})
                return
            self.answerOK({"status":"free"})
            return
        elif dictData['type'] == "quit":
            labs = tb.get_lab(init_academy=user['ID'], over=False)
            if len(labs) == 0:
                labs = tb.get_lab(invited_academy=user['ID'], over=False)
                if len(labs) == 0:
                    self.errorRoutine("This academy is not currently part of a lab")
                    return
            tb.update_labs(ID=labs[0]['ID'], over=True)
            self.answerOK({})
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
