import json
import mysql.connector
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
