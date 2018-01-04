import os
import re

ifconfig = os.popen("ifconfig -a").read().splitlines()

print (ifconfig)

for line in ifconfig:
	m = re.search('^([a-z]+)\s+Link encap:([a-zA-Z]+)', line)
	print (m)
#lo        Link encap:Local Loopback  
#          inet addr:127.0.0.1  Mask:255.0.0.0
#          inet6 addr: ::1/128 Scope:Host
#          UP LOOPBACK RUNNING  MTU:65536  Metric:1
#          RX packets:3931 errors:0 dropped:0 overruns:0 frame:0
#         TX packets:3931 errors:0 dropped:0 overruns:0 carrier:0
#          collisions:0 txqueuelen:1 
#          RX bytes:1988941 (1.8 MiB)  TX bytes:1988941 (1.8 MiB)
