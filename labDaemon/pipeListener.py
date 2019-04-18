import sys, os, iptc, grp
from pathlib import Path
import threading
from config import *
import errno
import socket

def occupied(filename):
    f = Path(filename)
    return f.exists()

def createPipe(filename):
    #Checks if the path already exists and deletes it if necessary
    if occupied(filename):
        os.remove(filename)
        if occupied(filename):
            print("Pipe cannot be created because something already exists")
            return False
    #At this point the path is free 
    os.mkfifo(filename, 0o660)
    if occupied(filename) == False:
        print("Cannot create pipe")
        return False
    tbgr = grp.getgrnam("twinbridge")
    os.chown(filename, -1, tbgr.gr_gid)
    os.chmod(filename, 0o620)
    return True

def delete_association(virt_ip):
    print("deleting association of", virt_ip)
    table_filter = iptc.Table(iptc.Table.FILTER)
    table_filter.Autocommit = False
    table_nat = iptc.Table(iptc.Table.NAT)
    table_nat.Autocommit = False

    chain_filter_FORWARD = iptc.Chain(table_filter, "VPN_FW")
    chain_nat_PREROUTING = iptc.Chain(table_nat, "PREROUTING")

    for rule in chain_filter_FORWARD.rules:
        if rule.src.split('/')[0]  == virt_ip\
                or rule.dst.split('/')[0] == virt_ip:
            chain_filter_FORWARD.delete_rule(rule)
            print("rule deleted")
    for rule in chain_nat_PREROUTING.rules:
        if rule.src.split("/")[0] == virt_ip\
                or rule.target.parameters.get("to_destination", "") == virt_ip:
            chain_nat_PREROUTING.delete_rule(rule)
            print("rule deleted")
    table_filter.commit()
    table_nat.commit()
    table_filter.autocommit = True
    table_nat.autocommit = True
    return True

class PipeListener(threading.Thread):
    def __init__(self, pipePath):
        threading.Thread.__init__(self)
        self.pipePath = pipePath
        if createPipe(self.pipePath) == False:
            raise FileNotFoundError(errno.EACCES, os.strerror(errno.EACCES), pipePath)
        
    def run(self):
        createPipe(self.pipePath)
        pipe = open(self.pipePath, "r")
        while 1:
            for address in pipe:
                address = address.strip()
                print("[" + address + "]")
                try:
                    socket.inet_aton(address)
                    delete_association(address)
                except:
                    print("not an address")
                    #address was not an IPv4 address
                    continue


if __name__ == "__main__":
    PIPE_PATH = "/tbpipe"
    listener = PipeListener(PIPE_PATH)
    listener.start()
