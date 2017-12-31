import socket
import fcntl
import struct

def get_ip_address(interface_name):
	"""
	Source: https://github.com/ActiveState/code/tree/master/recipes/Python/439094_get_IP_address_associated_network_interface
	get the IP address associated with a network interface (linux only)
	Originally published: 2005-08-11 13:30:18
	Last updated: 2005-08-11 13:30:18
	Author: paul cannon

	Uses the Linux SIOCGIFADDR ioctl to find the IP address associated with a network interface, 
	given the name of that interface, e.g. "eth0". 
	The address is returned as a string containing a dotted quad.
	"""
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', interface_name[:15])
	)[20:24])
