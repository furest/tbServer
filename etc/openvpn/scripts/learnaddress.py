#!/usr/bin/env python3
import sys,mysql.connector,time,os,datetime
import fcntl

def send_delete(virt_ip, pipename):
    print("sending delete...")
    try:
        f = os.open(pipename, os.O_WRONLY | os.O_NONBLOCK)
        virt_ip+= "\n"
        os.write(f, virt_ip.encode())
        print("delete sent!")
    except Exception as e:
        print("Error!", e)
    finally:
        os.close(f)
def add_ip(cn, virt_ip,real_ip, real_port):
    tm = time.time()
    timestamp = datetime.datetime.fromtimestamp(tm).strftime('%Y-%m-%d %H:%M:%S')
    val = (cn, timestamp, virt_ip, real_ip, real_port)
    dbcurs.execute(add_ip_statement,val)
    db.commit();

def del_ip(virt_ip):
    dbcurs.execute(del_ip_statement, virt_ip)
    db.commit();

PIPE = "/tbpipe"
print("UID", os.getuid(), " : EUID", os.geteuid())
print("GID", os.getgid(), " : EGID", os.getegid())
current_mode = sys.argv[1]
client_v_ip = sys.argv[2]
client_r_ip = os.environ.get('trusted_ip', 'unknown')
client_r_port = os.environ.get('trusted_port', '0')

db = mysql.connector.connect(
        host="localhost",
        user="vpn",
        password="vpnpassword",
        database="twinbridge"
)

dbcurs = db.cursor()
add_ip_statement = "INSERT INTO CONNECTED_CLIENTS(username, connection_timestamp, virt_ip, real_ip, real_port) VALUES (%s,%s,%s,%s,%s)"
del_ip_statement = "DELETE FROM CONNECTED_CLIENTS WHERE virt_ip = %s"

print(current_mode, client_v_ip)
if(current_mode == "delete"):
    del_ip((client_v_ip,))
    send_delete(client_v_ip, PIPE)
    sys.exit(0)
client_cn = sys.argv[3]
if(current_mode == "update"):
    del_ip((client_v_ip,))
    send_delete(client_v_ip, PIPE)
add_ip(client_cn, client_v_ip, client_r_ip, client_r_port)

sys.exit(0)
