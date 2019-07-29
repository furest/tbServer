#Python imports
import mysql.connector

#Project imports
from includes.config import *

def get_tuple(table, **data):
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    req = "SELECT * FROM " + table
    need_and=False
    req_tuple=()
    for param in data:
        if need_and:
            req += " AND "
        else:
            req += " WHERE "
        if data[param] == None:
            req += param + "IS NULL"
        elif data[param] == "NOTNULL":
            req += param + "IS NOT NULL"
        else:
            req += param + " = %s"
        req_tuple = req_tuple + (data[param],)
        need_and=True
    c.execute(req, req_tuple)
    results = c.fetchall()
    return results

def get_lab_stats(**data):
    return get_tuple("laborations_statistics", **data)

def get_connected_client(**data):
   return get_tuple("connected_clients", **data)
   # db = mysql.connector.connect(**tbParams)
   # c = db.cursor(dictionary=True)
   # req = "SELECT * FROM connected_clients "
   # need_and = False
   # req_tuple = ()
   # if ID != None:
   #     req += "WHERE ID = %s"
   #     req_tuple=(ID,)
   #     need_and = True
   # if virt_ip != None:
   #     if need_and:
   #         req +=" AND "
   #     else:
   #         req += " WHERE "
   #     req += " virt_ip = %s "
   #     req_tuple = req_tuple + (virt_ip,)
   #     need_and = True
   # if real_ip != None:
   #     if need_and:
   #         req +=" AND "
   #     else:
   #         req += " WHERE "
   #     req += " real_ip = %s "
   #     req_tuple = req_tuple + (real_ip,)
   #     need_and = True
   # if real_port != None:
   #     if need_and:
   #         req +=" AND "
   #     else:
   #         req += " WHERE "
   #     req += " real_port = %s "
   #     req_tuple = req_tuple + (real_port,)
   #     need_and = True
   # c.execute(req, req_tuple)
   # users = c.fetchall()
   # return users

def get_lab(**data):
    return get_tuple("laborations", **data)
   # db = mysql.connector.connect(**tbParams)
   # c = db.cursor(dictionary=True)
   # req = "SELECT * FROM laborations"
   # need_and=False
   # req_tuple = ()
   # if ID != None:
   #     req += " WHERE ID = %s"
   #     req_tuple=(ID,)
   #     need_and = True
   # if pin != None:
   #     if need_and:
   #         req +=" AND "
   #     else:
   #         req += " WHERE "
   #     req += " pin = %s "
   #     req_tuple = req_tuple + (pin,)
   #     need_and = True
   # if init_academy != None:
   #     if need_and:
   #         req +=" AND "
   #     else:
   #         req += " WHERE "
   #     req += " init_academy = %s "
   #     req_tuple = req_tuple + (init_academy,)
   #     need_and = True
   # if invited_academy != None:
   #     if need_and:
   #         req +=" AND "
   #     else:
   #         req += " WHERE "
   #     req += " invited_academy = %s "
   #     req_tuple = req_tuple + (invited_academy,)
   #     need_and = True
   # if started_at != None:
   #     if need_and:
   #         req +=" AND "
   #     else:
   #         req += " WHERE "
   #     req += " started_at = %s "
   #     req_tuple = req_tuple + (started_at,)
   #     need_and = True
   # if over != None:
   #     if need_and:
   #         req +=" AND "
   #     else:
   #         req += " WHERE "
   #     req += " over = %s "
   #     req_tuple = req_tuple + (over,)
   #     need_and = True
   # c.execute(req, req_tuple)
   # labs = c.fetchall()
   # return labs

def delete_connected_client(ID):
    return delete_tuple("connected_clients", ID)

def delete_lab(ID):
    return delete_tuple("laborations", ID)

def delete_tuple(table, ID):
    if table == None or ID == None:
        return False
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    req = "DELETE FROM " + table + " WHERE ID=%s"
    try:
        c.execute(req, (ID,))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return True

def insert_connected_client(ID, virt_ip=None, real_ip=None, real_port=None):
    if ID == None:
        return False
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    req = "INSERT INTO connected_clients (ID, virt_ip, real_ip, real_port) VALUES (%s, %s, %s, %s)"
    req_tuple = (ID, virt_ip, real_ip, real_port)
    try:
        c.execute(req, req_tuple)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    return ID
    

def insert_lab(init_academy, pin=None, invited_academy=None, over=False):
    if init_academy == None or pin == None:
        return False
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    req = "INSERT INTO laborations (pin, init_academy, invited_academy, over) VALUES (%s,%s,%s,%s)"
    req_tuple = (pin, init_academy, invited_academy, over)
    db.commit()
    try:
        c.execute(req, req_tuple)
        lastrowid = c.lastrowid
        db.commit()
        return lastrowid
    except Exception as e:
        db.rollback()
        raise e


def update_connected_client(ID, **data):
    """
    Updates the connected user with the current ID.
    Fields to update must be passed as arguments : field1=newvalue.
    To set a field to NULL : field1=None
    To leave a field untouched don't include it in the parameters
    CAUTION : does not check whether fields exist in the table
    """
    return update_tuple("connected_clients", ID, **data)

def update_labs(ID, **data):
    """
    Updates the laboration with the current ID.
    Fields to update must be passed as arguments : field1=newvalue.
    To set a field to NULL : field1=None
    To leave a field untouched don't include it in the parameters
    CAUTION : does not check whether fields exist in the table
    """
    return update_tuple("laborations", ID, **data)

def update_tuple(table, ID, **data):
    """
    Updates the tuble with the current ID.
    Fields to update must be passed as arguments : field1=newvalue.
    To set a field to NULL : field1=None
    To leave a field untouched don't include it in the parameters
    CAUTION : does not check whether fields exist in the table
    """
    if ID == None or table == None:
        return False
    if len(data) == 0:
        return True
    db = mysql.connector.connect(**tbParams)
    c = db.cursor(dictionary=True)
    req = "UPDATE "+ table +" SET "
    need_comma = False
    req_tuple = ()
    for field in data:
        if need_comma:
            req += ","
        req += field+"= %s"
        req_tuple = req_tuple + (data[field],)
        need_comma = True
    req += " WHERE ID=%s"
    req_tuple = req_tuple + (ID,)
    try:
        c.execute(req, req_tuple)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return True

