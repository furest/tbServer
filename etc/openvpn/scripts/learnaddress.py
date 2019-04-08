#!/usr/bin/env python3
import sys,mysql.connector,time,os,datetime

def add_ip(cn, virt_ip,real_ip, real_port):
    tm = time.time()
    timestamp = datetime.datetime.fromtimestamp(tm).strftime('%Y-%m-%d %H:%M:%S')
    val = (cn, timestamp, virt_ip, real_ip, real_port)
    dbcurs.execute(add_ip_statement,val)
    db.commit();

def del_ip(virt_ip):
    dbcurs.execute(del_ip_statement, virt_ip)
    db.commit();


current_mode = sys.argv[1]
client_v_ip = sys.argv[2]
client_r_ip = os.environ.get('trusted_ip', 'unknown')
client_r_port = os.environ.get('trusted_port', '0')

db = mysql.connector.connect(
        host="localhost",
        user="admin",
        password="AkyP3neGFaB689eK",
        database="netacad_exchange"
)

dbcurs = db.cursor()

add_ip_statement = "INSERT INTO NE_CONNECTED_CLIENTS(cn, conn_time, v_ip, ip, port) VALUES (%s,%s,%s,%s,%s)"
del_ip_statement = "DELETE FROM NE_CONNECTED_CLIENTS WHERE V_IP = %s"

if(current_mode == "delete"):
    del_ip((client_v_ip,))
    sys.exit(0)
client_cn = sys.argv[3]
if(current_mode == "update"):
    del_ip((client_v_ip,))
add_ip(client_cn, client_v_ip, client_r_ip, client_r_port)

sys.exit(0)
