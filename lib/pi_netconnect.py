#import logging
import socket
import netifaces
import threading
import select
import sqlite3

from pprint import pprint
from time import sleep, time
from netaddr import IPNetwork, IPAddress

from lib._logging import logger as logging
from lib.pi_utilities import pi_revision, pi_serialnumber
from lib.database_utils import update_node

class UDPBeacon:
    def __init__(self,message="PiControl_beacon",port=31415,interval=60):
        '''
        Initialiation method
        '''
        self.port      = port
        self.interval  = interval
        self.message   = message
        self.status    = "initialized"
        self.last_scan = int(time())-self.interval-5
        logging.debug('Beacon initialized...')

    def stop(self):
        '''
        stop beacon loop thread
        '''
        logging.debug('stop() called...')
        logging.warn('Stopping UDPBeacon sender thread')
        self.looping = False
        self.status  = "stopped"

    def start(self):
        '''
        start beacon loop thread
        '''
        logging.warn('Starting UDPBeacon sender thread')
        logging.debug('start() called...')
        self.looping = True
        self.thread = threading.Thread(name='udp_beacon_sender', target=self._loop)
        self.thread.daemon = True
        self.thread.start()
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
        logger.warn('Sending UDP Beacons to UDP port ' + str(self.port))
        while self.looping:
            revision = pi_revision()
            hostname = socket.gethostname()
            serialnumber = pi_serialnumber(type='text')
            if self.last_scan + self.interval >= int(time()):
                logging.debug("\n"
                            + 'Current time  : ' + str(int(time())) + "\n"
                            + 'Last scan time: ' + str(self.last_scan) + "\n"
                            + 'Interval      : ' + str(self.interval) + "\n"
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
                                    hbSocket.sendto(str(self.message + ';' + hostname + ';' + revision + ';' + serialnumber), (str(IPAddress(ip)), self.port))
            sleep(self.interval)
        self.thread.join(1)

class UDPBeaconListener:
    def __init__(self,message="PiControl_beacon",port=31415):
        '''
        Initialiation method
        '''
        self.status         = "initialized"
        self.port           = port
        self.message        = message
        logging.debug('UDPBeaconListener initialized...')

    def stop(self):
        '''
        stop UDPBeaconListener loop thread
        '''
        logging.debug('stop() called...')
        logging.warn('Stopping UDPBeaconListener thread')
        self.looping = False
        self.status  = "stopped"

    def start(self):
        '''
        start UDPBeaconListener loop thread
        '''
        logging.warn('Starting UDPBeaconListener thread')
        logging.debug('start() called...')
        self.looping = True
        self.thread = threading.Thread(name='udp_beacon_listener', target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        self.status  = "running"

    def _loop(self):
        '''
        loop until self.looping == False
        '''
        logging.debug( '_loop() called...' )
        logging.debug( 'Listening for UDPBeacons from external clients...' )
        hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        hbSocket.bind(('0.0.0.0', self.port))
        logger.warn('Listening for UDP Beacons on UDP port ' + str(self.port))
        while self.looping:
            (rfd,wfd,efd) = select.select([hbSocket],[],[])
            if hbSocket in rfd:
                (string, address) = hbSocket.recvfrom(100)
                #skip loopback connections
                if address == '127.0.0.1':
                    continue
                message, hostname, revision, serialnumber = string.split(';')
                if message == self.message:
                    #TODO: Add responding clients to database
                    ipaddress    = str(address[0])
                    hostname     = str(hostname)
                    revision     = str(revision)
                    serialnumber = str(serialnumber)
                    last_checkin = str( int( time() ) )
                    logging.debug('Beacon received from ' + str(address[0]) + ' (' + serialnumber + ')')
                    update_node(ipaddress, hostname, revision, serialnumber, last_checkin)
            sleep(0.1)
        self.thread.join(1)
