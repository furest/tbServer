import os, sys
os.setgid(1004)
os.setegid(1004)
os.setuid(65534)
os.seteuid(65534)
f = open("/tbpipe", "w")
addr = sys.argv[1]
f.write(addr)

