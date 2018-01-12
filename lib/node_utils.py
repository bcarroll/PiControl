# coding=utf-8
import socket
import requests
import json
from flask import jsonify

from lib.database_utils import get_nodes
from lib._logging import logger

def node_cpu_usage():
    get_data_from_nodes('/dashboard/cpu_usage')
    return jsonify({'cpu_usage': node_data})

def get_data_from_nodes(URI):
    nodes = get_nodes(type='list')
    # Add local node to list of nodes
    nodes.append({"ipaddress": '127.0.0.1', "hostname": socket.gethostname(), "last_checkin": ""})
    node_data = []
    node_data.append(node_chart_data)
    # Add data from discovered nodes
    for node in nodes:
        node_url = 'https://' + node['ipaddress'] + ':31415' + URI
        try:
            r = requests.get(node_url, verify=False)
            if r.status_code != 200:
                logger.warn(node_url + ' returned ' + r.status_code)
            node_chart_data = {
                    "ipaddress": node['ipaddress'],
                    "hostname": node['hostname'],
                    "last_checkin": node['last_checkin'],
                    "data": r.json()
                }
            node_data.append(node_chart_data)
        except:
            logger.warn('Error accessing ' + node_url)
            node_chart_data = {
                    node['ipaddress']: ""
                }
            node_data.append(node_cpu_usage_data)
    return(node_data)

