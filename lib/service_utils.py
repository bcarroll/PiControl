# coding=utf-8
import os
from flask import jsonify

def get_service_status():
    '''
    Returns a dict with a list of service names and status
    '''
    services = {}
    # get all services, convert to a list
    services = os.popen("service --status-all").read().splitlines()
    for service in services:
        # remove left brackets
        service.replace('[','')
        status,name = service.split(']')
        status = status.trim()
        name = name.trim()
        if status == '-':
            status = 'off'
        elif status == '+':
            status = 'on'
        services[name] = status
    return(services)
