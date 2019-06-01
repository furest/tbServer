import sys, os, iptc, grp
from pathlib import Path
import threading
from config import *
import errno
import socket
from methods import *
from makeAssociation import *
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

class PipeListener(threading.Thread):
    def __init__(self, pipePath):
        threading.Thread.__init__(self)
        self.pipePath = pipePath
        if createPipe(self.pipePath) == False:
            raise FileNotFoundError(errno.EACCES, os.strerror(errno.EACCES), pipePath)
        
    def run(self):
        createPipe(self.pipePath)
        while True:
            with open(self.pipePath, "rt") as pipe:
                while True:
                    address = pipe.readline()
                    address = address.strip()
                    if address == "":
                        break
                    print("[" + address + "]")
                    try:
                        socket.inet_aton(address)
                        delete_association(address)
                    except Exception as e:
                        print("not an address")
                        #address was not an IPv4 address
                        print(e)
                        continue


if __name__ == "__main__":
    PIPE_PATH = "/tbpipe"
    listener = PipeListener(PIPE_PATH)
    listener.start()
