# coding=utf-8

from flask import Response
from lib.database_utils import get_nodes

def node_cpu_usage():
    nodes = get_nodes(type='list')
    print("NODES:")
    for node in nodes:
        print(node['ipaddress'] + ', ' + node['hostname'] + ', ' + node['last_checkin'])
