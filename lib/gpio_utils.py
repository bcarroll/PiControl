# coding=utf-8

import os
from flask import jsonify
from lib._logging import logger

def gpio_info():
    gpio_info = ['ERROR']
    try:
        gpio_info = os.popen("gpio readall|grep -v '\-\-\-'| grep -v 'Physical'|tr -s ' ' 2>/dev/null").read().replace('||', '|').splitlines()
    except:
        logger.error('Error getting gpio_info')
    pins = {}
    for line in gpio_info:
        undef,BCM,wPi,Name,Mode,V,Physical,Physical2,V2,Mode2,Name2,wPi2,BCM2,undef2 = line.replace(' ', '').split('|')
        if V is "0" or V is "0.0":
            V = "0v"
        if V is "1":
            V = "3.3v"

        pins[Physical] = {
            'bcm_pin': BCM,
            'wPi_pin': wPi,
            'name': Name,
            'mode': Mode,
            'v': V,
        }
        pins[Physical2] = {
            'bcm_pin': BCM2,
            'wPi_pin': wPi2,
            'name': Name2,
            'mode': Mode2,
            'v': V2,
        }
    return jsonify(pins)

def set_gpio_mode(pin,mode):
    result = False
    try:
        os.popen('gpio mode ' + pin + " " + mode).read()
        result = True
    except:
        result = False
    logger.debug('set_gpio_mode(' + str(pin) + ',' + str(mode) + ') returned ' + str(result))
    return( jsonify(result) )

def set_gpio_pin(pin, status):
    result = False
    try:
        os.popen('gpio write ' + int(pin) + ' ' + int(status))
        result = True
    except:
        result = False
    logger.debug('set_gpio_pin(' + str(pin) + ',' + str(status) + ') returned ' + str(result))
    return( jsonify(result) )
