# coding=utf-8

import requests

from flask import jsonify

from lib.database_utils import get_nodes
from lib._logging import logger

def node_cpu_usage():
    nodes = get_nodes(type='list')
    node_data = []
    for node in nodes:
        print(node['ipaddress'] + ', ' + node['hostname'] + ', ' + node['last_checkin'])
        node_url = 'https://' + node['ipaddress'] + ':31415/dashboard/cpu_usage'
        try:
            r = requests.get(node_url)
            if r.status_code != 200:
                logger.warn(node_url + ' returned ' + r.status_code)
            node_cpu_usage_data = {
                    "ipaddress": node['ipaddress'],
                    "hostname": node['hostname'],
                    "last_checkin": node['last_checkin'],
                    "data": r.json
                }
            node_data.append(node_cpu_usage_data)
        except:
            logger.warn('Error accessing ' + node_url)
            node_cpu_usage_data = {
                    node['ipaddress']: ""
                }
            node_data.append(node_cpu_usage_data)
    return jsonify({'cpu_usage': node_data})

