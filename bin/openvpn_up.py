#!/usr/bin/python3
#Python imports
import os, sys
from scapy.all import *
from netaddr import IPNetwork, IPAddress
import multiprocessing  

#Project imports
from includes.config import config
os.environ['PATH'] = '/usr/bin:/usr/sbin:/sbin:/bin'
os.environ['XTABLES_LIBDIR'] = config['XTABLES_LIBDIR']
from includes.makeAssociation import delete_association
import includes.twinbridge_access as tb


def check_client_connected(client_tuple):
    p = IP(dst=client_tuple['virt_ip'])/ICMP()
    ret = sr1(p, timeout=config['UP_TIMEOUT'])
    if ret == None:
        print(f"client {client_tuple['virt_ip']} offline")
        return client_tuple
    else:
        print(f"client {client_tuple['virt_ip']} online")



if __name__ == "__main__":
    int_ip = sys.argv[4]
    int_mask = sys.argv[5]
    srv_net = IPNetwork(f"{int_ip}/{int_mask}")
    clients = tb.get_connected_client()

    with multiprocessing.Pool(10) as p:
        unreachable_clients_ids = p.map(check_client_connected,[client for client in clients if client['virt_ip'] in srv_net])

    for client in [client for client in unreachable_clients_ids if client != None]:
        tb.delete_connected_client(client['ID'])
        #It is actually possible to delete the association from this script as this is executed before the uid change
        delete_association(client['virt_ip'])









