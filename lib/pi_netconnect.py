# coding=utf8
import socket
import netifaces
import threading
import select
import sqlite3
import hashlib

from pprint import pprint
from time import sleep, time
from netaddr import IPNetwork, IPAddress

from lib._logging import logger
from lib.pi_utilities import pi_revision, pi_serialnumber
from lib.database_utils import update_node
from lib.database_config import get_config

def hash_key(key):
    key = hashlib.sha256(key.encode('utf-8')).hexdigest()
    return(key)

def validate_hash(string, hash):
    if hash_key(string)[0:-48] == hash[0:-48]:
        return(True)
    else:
        return(False)

class UDPBeacon:
    def __init__(self,message="PiControl_beacon",port=31415):
        '''
        Initialiation method
        '''
        self.port      = port
        self.message   = message
        self.status    = "initialized"
        self.last_scan = int(time())-int(get_config()['beacon_interval'])-5
        self.looping   = False
        logger.debug('Beacon initialized...')

    def stop(self):
        '''
        stop beacon loop thread
        '''
        logger.debug('stop() called...')
        logger.info('Stopping UDPBeacon sender thread')
        self.looping = False
        self.status  = "stopped"

    def start(self):
        '''
        start beacon loop thread
        '''
        logger.info('Starting UDPBeacon sender thread')
        logger.debug('start() called...')
        if get_config()['beacon_sender_enabled'] == False:
            logger.warn('Beacon Sender is disabled')
            self.stop()
        self.looping = True
        self.thread  = threading.Thread(name='udp_beacon_sender', target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        self.status  = "running"

    def _loop(self):
        '''
        Send a UDP message to all devices on all connected networks
        If PiControl is running on the destination device, it will answer back
        loop until self.looping == False
        '''
        logger.debug( 'UDPBeacon _loop() started...' )
        #keep track of the ip addresses we have already scanned
        ip_list = []
        logger.info('Sending UDP Beacons to UDP port ' + str(self.port))
        while self.looping:
            if get_config()['beacon_sender_enabled'] == False:
                self.stop()
            revision = pi_revision()
            hostname = socket.gethostname()
            serialnumber = pi_serialnumber(type='text')
            interval = int(get_config()['beacon_interval'])
            if self.last_scan + interval >= int(time()):
                logger.debug("\n"
                            + 'Current time  : ' + str(int(time())) + "\n"
                            + 'Last scan time: ' + str(self.last_scan) + "\n"
                            + 'Interval      : ' + str(interval) + "\n"
                            + 'Elapsed time  : ' + str(int(time())-self.last_scan)
                    )
            else:
                logger.debug('Generating UDPBeacons...')
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
                            if ip_info['addr'] == '127.0.0.1':
                                continue
                            #get all the ipaddresses in the ipaddress' network
                            ip_cidr      = IPNetwork(ip_info['addr'] + '/' + ip_info['netmask']).cidr
                            logger.debug('Sending UDPBeacon to ' + str(ip_cidr))
                            if str(ip_cidr) in ip_list:
                                logger.debug("skipping " + str(ip_cidr))
                                continue
                            #add the current network to the list of networks that have been scanned
                            ip_list.append(str(ip_cidr))
                            for ip in ip_cidr:
                                #skip the network, broadcast, and local addresses
                                if (ip != ip_cidr.network) and (ip != ip_cidr.broadcast) and (str(IPAddress(ip)) != ip_info['addr']):
                                    logger.debug('Sending UDPBeacon to ' + str(IPAddress(ip)))
                                    try:
                                        secret_key = get_config()['secret_key']
                                        hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                        hbSocket.sendto(str(self.message) + ';' + str(hostname) + ';' + str(revision) + ';' + str(serialnumber) + ';' + hash_key(secret_key), (str(IPAddress(ip)), self.port))
                                    except Exception as e:
                                        logger.error(e.message)
                                    sleep(0.1)
            sleep( int(get_config()['beacon_interval']) )
        self.thread.join(1)

class UDPBeaconListener:
    def __init__(self,message="PiControl_beacon",port=31415):
        '''
        Initialiation method
        '''
        self.status         = "initialized"
        self.port           = port
        self.message        = message
        self.looping        = False
        logger.debug('UDPBeaconListener initialized...')

    def stop(self):
        '''
        stop UDPBeaconListener loop thread
        '''
        logger.debug('stop() called...')
        logger.info('Stopping UDPBeaconListener thread')
        self.looping = False
        self.status  = "stopped"

    def start(self):
        '''
        start UDPBeaconListener loop thread
        '''
        logger.info('Starting UDPBeaconListener thread')
        logger.debug('start() called...')
        if get_config()['beacon_listener_enabled'] == False:
            logger.warn('Beacon Listener is disabled')
            self.stop()

        self.looping = True
        self.thread = threading.Thread(name='udp_beacon_listener', target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        self.status  = "running"

    def _loop(self):
        '''
        loop until self.looping == False
        '''
        logger.debug( '_loop() called...' )
        logger.info( 'Listening for UDPBeacons from external clients...' )
        hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        hbSocket.bind(('0.0.0.0', self.port))
        logger.warn('Listening for UDP Beacons on UDP port ' + str(self.port))
        while self.looping:
            if get_config()['beacon_listener_enabled'] == False:
                self.stop()
            try:
                (rfd,wfd,efd) = select.select([hbSocket],[],[])
                if hbSocket in rfd:
                    (string, address) = hbSocket.recvfrom(100)
                    #skip loopback connections
                    if address == '127.0.0.1':
                        continue
                    message, hostname, revision, serialnumber, secret_key = string.split(';')
                    if message == self.message:
                        ipaddress    = str(address[0])
                        hostname     = str(hostname)
                        revision     = str(revision)
                        serialnumber = str(serialnumber)
                        secret_key   = str(secret_key)
                        last_checkin = str( int( time() ) )
                        logger.debug('Beacon received from ' + str(address[0]) + ' (' + serialnumber + ')')
                        print('Received: ' + secret_key)
                        print('Expected: ' + hash_key(get_config()['secret_key']))
                        if validate_hash(secret_key, hash_key(get_config()['secret_key'])):
                            update_node(ipaddress, hostname, revision, serialnumber, secret_key, last_checkin)
                        else:
                            logger.info(str(address[0]) + ' is not an authorized PiControl node')
            except Exception as e:
                logger.error(e.message)
            sleep(0.1)
        self.thread.join(1)
