# coding=utf-8

import requests

from flask import jsonify

from lib.database_utils import get_nodes

def node_cpu_usage():
    nodes = get_nodes(type='list')
    node_data = []
    for node in nodes:
        print(node['ipaddress'] + ', ' + node['hostname'] + ', ' + node['last_checkin'])
        try:
            node_url = 'https://' + node['ipaddress'] + ':31415/dashboard/cpu_usage'
            r = requests.get(node_url)
            if r.status_code != 200:
                logger.warn(node_url + ' returned ' + r.status_code)
            node_data = {
                ipaddress: r.text
            }
            node_data.append(node_data)
    return jsonify({'cpu_usage': node_data})

