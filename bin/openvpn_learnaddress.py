#!/usr/bin/python3
#Python imports
import sys, time, os, datetime
import fcntl

#Project imports
import includes.wordpress_access as wp
import includes.twinbridge_access as tb
from includes.config import *

def write_pipe(method, data):
    f = None
    try: 
        f = os.open(config['PIPE_PATH'], os.O_WRONLY | os.O_NONBLOCK)
        req = method + " " + data + "\n"
        os.write(f, req.encode())
    except Exception as e:
        print("Error!", e)
    finally:
        if f != None:
            os.close(f)


if __name__ == "__main__":
    current_mode = sys.argv[1]
    client_virt_ip = sys.argv[2]
    client_r_ip = os.environ.get('trusted_ip', 'unknown')
    client_r_port = os.environ.get('trusted_port', '0')
    client_email = None
    if len(sys.argv) > 3:
        client_email = sys.argv[3]


    print("--NEW CONNECTION--")
    print("Mode = " + current_mode)
    print("virt_ip = " + client_virt_ip)

    if current_mode == "add" or current_mode == "update":
        users = wp.get_user(email=client_email)
        if len(users) == 0:
            #Oops, user does not exist
            sys.exit(1)
        user = users[0]
        
        if current_mode == "update":
            connected_client = tb.get_connected_client(ID=user['ID'])
            if connected_client[0]['virt_ip'] != client_virt_ip:
                #Stop routing if virt_ip has changed
                write_pipe("DELETE", connected_client['virt_ip'])
            tb.update_connected_client(ID=connected_client[0]['ID'], virt_ip = client_virt_ip, real_port = client_r_port, real_ip = client_r_ip)
        else:
             tb.insert_connected_client(user['ID'], client_virt_ip, client_r_ip, client_r_port)

        labs = tb.get_lab(init_academy=user['ID'], over=False)
        other_user_id = None
        if len(labs) == 0:
            labs = tb.get_lab(invited_academy=user['ID'], over=False)
            if len(labs) == 0:
                #User isn't part of a lab. Simply exit with success
                sys.exit(0)
            else:
                other_user_id = labs[0]['init_academy']
        else:
            other_user_id = labs[0]['invited_academy']
        if other_user_id == None:
            #Lab has only one user. Quit
            sys.exit(0)
        other_user = tb.get_connected_client(ID=other_user_id)
        if len(other_user) == 0:
            #Other user is disconnected. Quit.
            sys.exit(0)
        write_pipe("ROUTE", client_virt_ip, other_useri[0]['virt_ip'])
        sys.exit(0)
    elif current_mode == "delete":
        connected_client = tb.get_connected_client(virt_ip=client_virt_ip)
        if len(connected_client) != 0:
            tb.delete_connected_client(connected_client[0]['ID'])
            write_pipe("DELETE", connected_client[0]['virt_ip'])
        sys.exit(0)

