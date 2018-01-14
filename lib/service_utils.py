# coding=utf-8
import os
from flask import jsonify

def get_service_status():
    '''
    Returns a dict with a list of service names and status
    '''
    services = {}
    # get all services, convert to a list
    service_list = os.popen("service --status-all").read().splitlines()
    for service in service_list:
        # remove left brackets
        status,name = service.split(']')
        status      = status.strip()
        name        = name.strip()
        if status == '[ -':
            status = 'off'
        elif status == '[ +':
            status = 'on'
        services[name] = status
    return(services)
