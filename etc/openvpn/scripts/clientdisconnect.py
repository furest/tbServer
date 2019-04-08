#!/usr/bin/env python3
import sys

sys.stdout = open('/ovpn/myoutput', 'a')
print(sys.argv[0])
print('Nb args: ' + str(len(sys.argv)))
for i in sys.argv:
    print('\t'+i)
print('IFCONFIG_POOL_LOCAL_IP=' + os.environ.get('ifconfig_pool_local_ip', 'none'))
print('IFCONFIG_POOL_REMOTE_IP=' + os.environ.get('ifconfig_pool_remote_ip', 'none'))

print("---------------------------")
sys.exit(0)
