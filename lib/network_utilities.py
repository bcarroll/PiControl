from flask import jsonify
import netifaces
from pprint import pprint

def get_interfaces():
	'''
	Return network interface information in JSON
	'''
	#https://pypi.python.org/pypi/netifaces
	interface_list = {}
	interfaces = netifaces.interfaces()
	for interface in interfaces:
		interface_list[interface] = {}
		addrs = netifaces.ifaddresses(interface)
		if addrs.has_key(netifaces.AF_INET):
			interface_list[interface]['ipv4'] = addrs[netifaces.AF_INET]
		if addrs.has_key(netifaces.AF_INET6):
			interface_list[interface]['ipv6'] = addrs[netifaces.AF_INET6]
		if addrs.has_key(netifaces.AF_LINK):
			interface_list[interface]['mac'] = addrs[netifaces.AF_LINK]
	return jsonify(interface_list)

if __name__ == '__main__':
	get_interfaces()