#!/usr/bin/env python3
import sys

sys.stdout = open('/ovpn/myoutput', 'a')
print(sys.argv[0])
print('Nb args: ' + str(len(sys.argv)))
for i in sys.argv:
    print('\t'+i)
print("---------------------------")
sys.exit(0)
