#Python imports
import mysql.connector
import random

#Project imports
from includes.config import *

def generatePin(length):
    random.seed(a=None)#Uses system current time
    pin = random.randint(10**(length-1), int("9"*length))
    return pin

def getLabDetails(labId):
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    c.execute("""SELECT 
                 lab.ID as lab_id,
                 lab.pin as lab_pin,
                 DATE_FORMAT(lab.started_at, "%Y-%m-%d %H:%i:%S") as lab_starttime,
                 lab.init_academy as init_id,
                 initacademy.virt_ip as init_ip,
                 lab.invited_academy as invit_id,
                 invitedacademy.virt_ip as invit_ip
                FROM laborations as lab
                LEFT JOIN connected_clients as initacademy ON initacademy.ID = lab.init_academy
                LEFT JOIN connected_clients as invitedacademy ON invitedacademy.ID = lab.invited_academy
                WHERE lab.ID = %s""", (labId,))
    lab = c.fetchone()
    return lab
