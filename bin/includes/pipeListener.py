#Python imports
import sys, os, iptc, grp
from pathlib import Path
import threading
import errno
import socket

#Project imports
from includes.config import *
from includes.methods import *
from includes.makeAssociation import *
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

def is_valid_address(address):
    try:
        socket.inet_aton(address)
        return True
    except Exception as e:
        return False


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
                    request = pipe.readline()
                    if request == "":
                        break
                    print("PIPE :", request)
                    request = request.strip()
                    args = request.split(" ")
                    print(args)
                    if len(args) == 0:
                        break
                    if args[0] == "DELETE":
                        if is_valid_address(args[1]):
                            delete_association(args[1])
                            print("deleted " + args[1])
                    elif args[0] == "ROUTE":
                        if len(args) < 3:
                            continue
                        if is_valid_address(args[1]) and is_valid_address(args[2]):
                            associate(args[1], args[2])
                            print("associated " + args[1] + " and " + args[2])


if __name__ == "__main__":
    PIPE_PATH = "/tbpipe"
    listener = PipeListener(PIPE_PATH)
    listener.start()
