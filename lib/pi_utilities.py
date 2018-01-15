# coding=utf8
import platform
import os
import re
import subprocess
from flask import jsonify
import psutil

from lib._logging import logger

########################################################################
# vcgencmd command references:
#https://elinux.org/RPI_vcgencmd_usage
#https://github.com/nezticle/RaspberryPi-BuildRoot/wiki/VideoCore-Tools
########################################################################

def cpu_count():
    '''
    Returns the number of CPUs in the system
    '''
    return jsonify({'cpu_count': psutil.cpu_count()})

def cpu_usage(per_cpu=True):
    '''
    Returns CPU usage in percent
    '''
    cpu_usage = 'ERROR'
    try:
        cpu_usage_list = psutil.cpu_percent(interval=1, percpu=per_cpu)
    except:
        logger.error('Error getting cpu_usage')
    return jsonify({'cpu_usage': cpu_usage_list})

def cpu_temperature(type='JSON'):
    '''
    Returns the core temperature in Celsius.
    https://github.com/nschloe/stressberry/blob/master/stressberry/main.py
    '''
    output = 'ERROR'
    try:
        output      = subprocess.check_output(['vcgencmd', 'measure_temp']).decode('utf-8')
    except:
        logger.error('Error getting cpu_temperature from vcgencmd')

    celcius     = output.replace('temp=', '').replace('\'C', '')
    try:
        fahrenheit  = float(format(float(celcius) * 9/5 + 32, '.1f'))
    except:
        fahrenheit = 'ERROR'
    temperature_string = str(fahrenheit) + ' F (' + str(celcius) + 'C)'
    if type == 'JSON':
        return jsonify(temp=temperature_string)
    elif type == 'fahrenheit':
        return (fahrenheit)
    elif type == 'celcius':
        return (celcius)
    elif type == 'text_fahrenheit':
        return jsonify(temp=fahrenheit)

def cpu_frequency():
    '''
    Returns the processor frequency in Hz.
    https://github.com/nschloe/stressberry/blob/master/stressberry/main.py
    '''
    output = 'ERROR'
    try:
        output = subprocess.check_output(['vcgencmd', 'measure_clock', 'arm']).decode('utf-8')
    except:
        logger.error('Error getting cpu_frequency')

    # frequency(45)=102321321
    m = re.match('frequency\\([0-9]+\\)=([0-9]+)', output)
    frequency = m.group(1)
    if frequency < 1000:
        frequency=frequency + 'Hz'
    elif frequency < 1000000:
        frequency=str(int(frequency)/1000) + 'Khz'
    elif frequency >= 1000000:
        frequency=str(int(frequency)/1000000) + 'Mhz'
    return jsonify (
            cpu_frequency=frequency
        )

def cpu_voltage():
    '''
    Returns the processor voltage
    '''
    output = 'ERROR'
    try:
        output = subprocess.check_output(['vcgencmd', 'measure_volts', 'core']).decode('utf-8')
    except:
        logger.error('Error getting cpu_voltage')

    voltage = output.replace('volt=', '').replace('V', '')
    return jsonify(
            cpu_volts=str(float(voltage)) + 'V'
        )

def av_codecs():
    '''
    Returns status of audio/video codecs (enabled/disabled)
    '''
    H264 = MPG2 = MPG4 = MJPG = MVC1 = WMV9 = '<tr><th></th><td>ERROR</td></tr>'
    try:
        H264 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'H264']).decode('utf-8') + '</td></tr>'
        MPG2 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'MPG2']).decode('utf-8') + '</td></tr>'
        MPG4 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'MPG4']).decode('utf-8') + '</td></tr>'
        MJPG = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'WMV9']).decode('utf-8') + '</td></tr>'
        WVC1 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'WVC1']).decode('utf-8') + '</td></tr>'
        WMV9 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'WMV9']).decode('utf-8') + '</td></tr>'
    except:
        logger.error('Error getting av_codecs')

    return(H264 + MPG2 + MPG4 + MJPG + WVC1 + WMV9).replace('=', '</th><td>')

def disk_usage():
    '''
    Return disk usage statistics
    '''
    output = '<th class="heading">Disk</th><td><table class="table-hover" style="width:100%;"><tr><td>ERROR</td></tr>'
    try:
        df = [s.split() for s in os.popen("df -Ph|grep -v Filesystem").read().splitlines()]
        output = '<th class="heading">Disk</th><td><table class="table-hover" style="width:100%;"><tr><th>Filesystem</th><th>Size</th><th>Used</th><th>Available</th><th>Use%</th><th>Mount Point</th></tr>'
        for line in range(0, len(df)):
            output = output + '<tr><td>' + df[line][0] + '</td><td>' + df[line][1] + '</td><td>' + df[line][2] + '</td><td>' + df[line][3] + '</td><td>' + df[line][4] + '</td><td>' + df[line][5] + '</td></tr>'
    except:
        logger.error('Error getting disk_usage')
    return(output + "</table></td>")

def disk_usage_summary():
    '''
    Return minimal disk usage statistics
    '''
    output = '<th class="heading">Disk</th><td><table class="table-hover" style="width:100%;"><tr><td>ERROR</td></tr>'
    try:
        df = [s.split() for s in os.popen("df -Ph|grep -v Filesystem|egrep -v '^tmpfs' 2>/dev/null").read().splitlines()]
        #output = '<th class="heading">Disk</th><td><table class="table-hover" style="width:100%;"><tr><th>Filesystem</th><th>Size</th><th>Used</th><th>Available</th><th>Use%</th><th>Mount Point</th></tr>'
        output = '<th class="heading"><i class="fas fa-hdd"></i> Disk</th><td><table class="table-hover" style="width:100%;text-align:center;"><tr><th>Mount Point</th><th>Available</th><th>Use%</th></tr>'
        for line in range(0, len(df)):
            #output = output + '<tr><td>' + df[line][0] + '</td><td>' + df[line][1] + '</td><td>' + df[line][2] + '</td><td>' + df[line][3] + '</td><td>' + df[line][4] + '</td><td>' + df[line][5] + '</td></tr>'
            output = output + '<tr><td> ' + df[line][5] + '</td><td> ' + df[line][3] + '</td><td> ' + df[line][4] + '</td></tr>'
    except:
        logger.error('Error getting disk_usage_summary')
    return(output + "</table></td>")

def pi_revision():
    '''
    Return the Raspberry Pi revision number
    https://www.raspberrypi-spy.co.uk/2012/09/checking-your-raspberry-pi-board-version/
    '''
    try:
        revision = os.popen("cat /proc/cpuinfo|grep '^Revision'|awk '{print $3}' 2>/dev/null").read().splitlines()
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
        serialnumber = os.popen("cat /proc/cpuinfo|grep '^Serial'|awk '{print $3}' 2>/dev/null").read().splitlines()
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
        return jsonify(pi[revision])
    else:
        return(pi[revision])

def process_list():
    return jsonify([p.info for p in psutil.process_iter(attrs=['pid', 'ppid', 'name', 'username'])])
