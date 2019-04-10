import json
import socketserver
from threading import *
import mysql.connector

tbParams = {
        "host": 'localhost',
        "user":'vpn',
        "passwd":'vpnpassword',
        "database":'twinbridge'
    }
wpParams = {
        "host": 'localhost',
        "user":'vpn',
        "passwd":'vpnpassword',
        "database":'wordpress'
    }
def listTwinings(client_id, dbParams):
    db = mysql.connector.connect(**dbParams)
    c = db.cursor(dictionary=True)
    client = (client_id, client_id)
#    c.execute("SELECT a1.user_login AS a1_login, a1.user_email AS a1_email, a1.id AS a1_id, a2.user_login AS a2_login, a2.user_email AS a2_email, a2.id AS a2_id, wp_twinings.id AS twining_id FROM wp_twinings INNER JOIN wp_users a1 ON a1.id = wp_twinings.academy_1 INNER JOIN wp_users a2 ON a2.id = wp_twinings.academy_2 WHERE a1.user_email = %s OR a2.user_email = %s ", client)
    c.execute("SELECT a1.user_login AS login,\
                    a1.user_email AS email,\
                    a1.id AS academy_id,\
                    wp_twinings.id AS twining_id\
            FROM wp_twinings\
            INNER JOIN wp_users a1 ON a1.id = wp_twinings.academy_1\
            INNER JOIN wp_users a2 ON a2.id = wp_twinings.academy_2\
            WHERE a2.user_email =  %s\
            UNION ALL\
            SELECT a2.user_login AS login,\
                    a2.user_email AS email,\
                    a2.id AS academy_id,\
                    wp_twinings.id AS twining_id\
            FROM wp_twinings\
            INNER JOIN wp_users a1 ON a1.id = wp_twinings.academy_1\
            INNER JOIN wp_users a2 ON a2.id = wp_twinings.academy_2\
            WHERE a1.user_email =  %s", client)
    twlist = c.fetchall()
    return twlist 

def errorRoutine(writable, message):
    jsonError = { "error":True, "message":message}
    writable.write(json.dumps(jsonError).encode())

def retrieveUser(dbParams, address):
    db = mysql.connector.connect(**dbParams)
    c = db.cursor(dictionary=True)
    ipClient = (address,)
    c.execute("SELECT * FROM CONNECTED_CLIENTS WHERE VIRT_IP = %s", ipClient)
    client = c.fetchone()
    return client



class labRequestHandler(socketserver.StreamRequestHandler):
    """
    Handles the requests.
    self.request = socket to the client
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
        except json.decoder.JSONDecodeError:
            errorRoutine(self.wfile,"Request is not a JSON object")
            return
        except:
            errorRoutine(self.wfile, "An unknown error occured")
            return 
        if not "type" in dictData:
            errorRoutine(self.wfile, "Request does not contain a type")
            return

        user = retrieveUser(tbParams, self.client_address[0])
        if(user == None):
            errorRoutine("IP is not bound to a user")
            return
        if dictData["type"] == "list":
            twiningsList = listTwinings(user["username"], wpParams)
            print("list twinings:", twiningsList)
            twiningsListStr = json.dumps(twiningsList) + "\n"
            self.wfile.write(twiningsListStr.encode())
            return
        else:
            errorRoutine("unknown request type")

if __name__ == "__main__":
    
    HOST, PORT = "172.16.100.1", 1500
    
    server = socketserver.ThreadingTCPServer((HOST, PORT), labRequestHandler)
    print("Server created. Now serving")
    server.serve_forever()
