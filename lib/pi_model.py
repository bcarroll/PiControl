# coding=utf-8

import os
from flask import jsonify

from lib._logging import logger

def pi_revision():
    '''
    Return the Raspberry Pi revision number
    https://www.raspberrypi-spy.co.uk/2012/09/checking-your-raspberry-pi-board-version/
    '''
    try:
        revision = os.popen("cat /proc/cpuinfo|grep '^Revision'|awk '{print $3}'").read().splitlines()
    except:
        logger.error('Error getting pi_revision')
    try:
        revision_string = revision[0]
    except:
        revision_string = ['ERROR']
    return(revision_string)

def pi_serialnumber(type='JSON'):
    '''
    Return the Raspberry Pi serial number
    '''
    try:
        serialnumber = os.popen("cat /proc/cpuinfo|grep '^Serial'|awk '{print $3}'").read().splitlines()
    except:
        logger.error('Error getting pi_serialnumber')
    if type == 'JSON':
        return jsonify(serialnumber=serialnumber)
    else:
        try:
            serialnumber_string = serialnumber[0]
        except:
            serialnumber_string = 'ERROR'
        return(serialnumber_string)

def pi_model(revision, type='JSON'):
    pi = {}
    pi['0002']   = {"model": "Model B v1.0","ram": "256MB"}
    pi['0003']   = {"model": "Model B v1.0","ram": "256MB"}
    pi['0004']   = {"model": "Model B v2.0","ram": "256MB"}
    pi['0005']   = {"model": "Model B v2.0","ram": "256MB"}
    pi['0006']   = {"model": "Model B v2.0","ram": "256MB"}
    pi['0007']   = {"model": "Model A v2.0","ram": "256MB"}
    pi['0008']   = {"model": "Model A v2.0","ram": "256MB"}
    pi['0009']   = {"model": "Model A v2.0","ram": "256MB"}
    pi['0010']   = {"model": "Model B+ v1.0","ram": "512MB"}
    pi['0011']   = {"model": "Compute Module v1.0","ram": "512MB"}
    pi['0012']   = {"model": "Model A+ v1.1","ram": "256MB"}
    pi['0013']   = {"model": "Model B+ v1.2","ram": "512MB"}
    pi['0014']   = {"model": "Compute Module v1.0","ram": "512MB"}
    pi['0015']   = {"model": "Model A+ v1.1","ram": "256MB"}
    pi['000d']   = {"model": "Model B v2.0","ram": "512MB"}
    pi['000e']   = {"model": "Model B v2.0","ram": "512MB"}
    pi['000f']   = {"model": "Model B v2.0","ram": "512MB"}
    pi['900021'] = {"model": "Model A+ v1.1","ram": "512MB"}
    pi['900032'] = {"model": "Model B+ v1.2","ram": "512MB"}
    pi['900092'] = {"model": "Zero v1.2","ram": "512MB"}
    pi['900093'] = {"model": "Zero v1.3","ram": "512MB"}
    pi['9000c1'] = {"model": "Zero W v1.1","ram": "512MB"}
    pi['920093'] = {"model": "Zero v1.3","ram": "512MB"}
    pi['a01040'] = {"model": "2 Model B v1.0","ram": "1GB"}
    pi['a01041'] = {"model": "2 Model B v1.1","ram": "1GB"}
    pi['a02082'] = {"model": "3 Model B v1.2","ram": "1GB"}
    pi['a020a0'] = {"model": "Compute Module 3 v1.0","ram": "1GB"}
    pi['a21041'] = {"model": "2 Model B v1.1","ram": "1GB"}
    pi['a22042'] = {"model": "2 Model B v1.2","ram": "1GB"}
    pi['a22082'] = {"model": "3 Model B v1.2","ram": "1GB"}
    pi['a32082'] = {"model": "3 Model B v1.2","ram": "1GB"}
    if type == 'JSON':
        return jsonify(pi[revision.lowercase()])
    else:
        return(pi[revision.lowercase()])
