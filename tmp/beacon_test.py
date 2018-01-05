import logging
import socket
import netifaces
import threading
import select
from pprint import pprint
from time import sleep, time
from netaddr import IPNetwork, IPAddress

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

class UDPBeacon:
    def __init__(self,message="PiControl_beacon",port=31415,interval=60000):
        "Initialiation method"
        self.port      = port
        self.interval  = interval
        self.message   = message
        self.status    = "initialized"
        self.last_scan = int(time())-(self.interval/1000)-5
        logging.debug('Beacon initialized...')

    def stop(self):
        "stop beacon loop thread"
        logging.debug('stop() called...')
        self.looping = False
        self.status  = "stopped"

    def start(self):
        "start beacon loop thread"
        logging.debug('start() called...')
        self.looping = True
        self.thread = threading.Thread(name='udp_beacon_sender', target=self._loop).start()
        self.status  = "running"

    def _loop(self):
        '''
        Send a UDP message to all devices on all connected networks
        If PiControl is running on the destination device, it will answer back
        loop until self.looping == False
        '''
        logging.debug( 'UDPBeacon _loop() started...' )
        #keep track of the ip addresses we have already scanned
        ip_list = []
        while self.looping:
            if self.last_scan + (self.interval/1000) >= int(time()):
                logging.debug("\n"
                            + 'Current time  : ' + str(int(time())) + "\n"
                            + 'Last scan time: ' + str(self.last_scan) + "\n"
                            + 'Interval      : ' + str(self.interval/1000) + "\n"
                            + 'Elapsed time  : ' + str(int(time())-self.last_scan)
                    )
            else:
                logging.debug('Generating UDPBeacons...')
                #clear the list of scanned ip addresses
                ip_list[:] = []
                #get a list of all the network interfaces
                interfaces = netifaces.interfaces()
                #iterate over each interface
                for interface in interfaces:
                    #skip the loopback interface
                    if interface == 'lo':
                        continue
                    #get all the ipaddresses assigned to each interface
                    addrs = netifaces.ifaddresses(interface)
                    #check for an ipaddress on the interface
                    if netifaces.AF_INET in addrs:
                        #iterate over each ipaddress on the interface
                        for ip_info in addrs[netifaces.AF_INET]:
                            #get all the ipaddresses in the ipaddress' network
                            ip_cidr      = IPNetwork(ip_info['addr'] + '/' + ip_info['netmask']).cidr
                            logging.debug('Sending UDPBeacon to ' + str(ip_cidr))
                            #skip ipaddresses that have already been scanned
                            logging.debug (ip_list)
                            if str(ip_cidr) in ip_list:
                                logging.debug("skipping " + str(ip_cidr))
                                continue
                            #add the current network to the list of networks that have been scanned
                            ip_list.append(str(ip_cidr))
                            for ip in ip_cidr:
                                #skip the network, broadcast, and local addresses
                                if (ip != ip_cidr.network) and (ip != ip_cidr.broadcast) and (str(IPAddress(ip)) != ip_info['addr']):
                                    #logging.debug('Sending UDPBeacon to ' + str(IPAddress(ip)))
                                    hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                    #hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                                    hbSocket.sendto(self.message, (str(IPAddress(ip)), self.port))
            sleep(self.interval/1000)

class UDPBeaconListener:
    def __init__(self,message="PiControl_beacon",port=31415):
        "Initialiation method"
        self.status         = "initialized"
        self.port           = port
        self.loop_iteration = 0
        self.message        = message
        logging.debug('UDPBeaconListener initialized...')

    def stop(self):
        "stop UDPBeaconListener loop thread"
        logging.debug('stop() called...')
        self.looping = False
        self.status  = "stopped"

    def start(self):
        "start UDPBeaconListener loop thread"
        logging.debug('start() called...')
        self.looping = True
        self.thread = threading.Thread(name='udp_beacon_listener', target=self._loop).start()
        self.status  = "running"

    def _loop(self):
        "loop until self.looping == False"
        logging.debug( '_loop() called...' )
        logging.debug( 'Listening for UDPBeacons from external clients...' )
        hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        hbSocket.bind((socket.gethostbyname(socket.gethostname()), self.port))
        while self.looping:
            (rfd,wfd,efd) = select.select([hbSocket],[],[])
            if hbSocket in rfd:
                (string, address) = hbSocket.recvfrom(100)
                #TODO: Add responding clients to database
                print ('--------------------------------')
                print ('string: %s' % string)
                print ('from: %s' % str(address))
                print ('--------------------------------')
            sleep(0.1)

if __name__ == '__main__':
    server = UDPBeaconListener()
    server.start()
    client = UDPBeacon()
    client.start()
