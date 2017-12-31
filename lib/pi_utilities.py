# coding=utf8
import os
import re
import subprocess
from flask import jsonify

########################################################################
# vcgencmd command references:
#https://elinux.org/RPI_vcgencmd_usage
#https://github.com/nezticle/RaspberryPi-BuildRoot/wiki/VideoCore-Tools
########################################################################

def cpu_usage():
    '''
    Returns CPU usage in percent
    '''
    cpu_percent_idle = os.popen("top -n1 | awk '/Cpu\(s\):/ {print $8}'").readline().strip()
    return(cpu_percent_idle)

def cpu_temperature():
    '''
    Returns the core temperature in Celsius.
    https://github.com/nschloe/stressberry/blob/master/stressberry/main.py
    '''
    output      = subprocess.check_output(['vcgencmd', 'measure_temp']).decode('utf-8')
    celcius     = output.replace('temp=', '').replace('\'C', '')
    fahrenheit  = float(celcius) * 9/5 + 32
    temperature_string = str(fahrenheit) + ' F (' + str(celcius) + 'C)'
    return jsonify(
            temp=temperature_string
        )

def cpu_frequency():
    '''
    Returns the processor frequency in Hz.
    https://github.com/nschloe/stressberry/blob/master/stressberry/main.py
    '''
    output = subprocess.check_output(['vcgencmd', 'measure_clock', 'arm']).decode('utf-8')

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
    output = subprocess.check_output(['vcgencmd', 'measure_volts', 'core']).decode('utf-8')
    voltage = output.replace('volt=', '').replace('V', '')
    return jsonify(
            cpu_volts=str(float(voltage)) + 'V'
        )

def av_codecs():
    '''
    Returns status of audio/video codecs (enabled/disabled)
    '''
    H264 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'H264']).decode('utf-8') + '</td></tr>'
    MPG2 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'MPG2']).decode('utf-8') + '</td></tr>'
    MPG4 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'MPG4']).decode('utf-8') + '</td></tr>'
    MJPG = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'WMV9']).decode('utf-8') + '</td></tr>'
    WVC1 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'WVC1']).decode('utf-8') + '</td></tr>'
    WMV9 = '<tr><th>' + subprocess.check_output(['vcgencmd', 'codec_enabled', 'WMV9']).decode('utf-8') + '</td></tr>'
    return(H264 + MPG2 + MPG4 + MJPG + WVC1 + WMV9).replace('=', '</th><td>')

def disk_usage():
    '''
    Return disk usage statistics
    '''
    df = [s.split() for s in os.popen("df -Ph|grep -v Filesystem").read().splitlines()]
    output = '<th class="heading">Disk</th><td><table class="table-hover" style="width:100%;"><tr><th>Filesystem</th><th>Size</th><th>Used</th><th>Available</th><th>Use%</th><th>Mount Point</th></tr>'
    for line in range(0, len(df)):
        output = output + '<tr><td>' + df[line][0] + '</td><td>' + df[line][1] + '</td><td>' + df[line][2] + '</td><td>' + df[line][3] + '</td><td>' + df[line][4] + '</td><td>' + df[line][5] + '</td></tr>'
    return(output + "</table></td>")

def disk_usage_summary():
    '''
    Return minimal disk usage statistics
    '''
    df = [s.split() for s in os.popen("df -Ph|grep -v Filesystem|egrep -v '^tmpfs'").read().splitlines()]
    #output = '<th class="heading">Disk</th><td><table class="table-hover" style="width:100%;"><tr><th>Filesystem</th><th>Size</th><th>Used</th><th>Available</th><th>Use%</th><th>Mount Point</th></tr>'
    output = '<th class="heading"><i class="fas fa-hdd"></i> Disk</th><td><table class="table-hover" style="width:100%;text-align:center;"><tr><th>Mount Point</th><th>Available</th><th>Use%</th></tr>'
    for line in range(0, len(df)):
        #output = output + '<tr><td>' + df[line][0] + '</td><td>' + df[line][1] + '</td><td>' + df[line][2] + '</td><td>' + df[line][3] + '</td><td>' + df[line][4] + '</td><td>' + df[line][5] + '</td></tr>'
        output = output + '<tr><td> ' + df[line][5] + '</td><td> ' + df[line][3] + '</td><td> ' + df[line][4] + '</td></tr>'
    return(output + "</table></td>")

def pi_model():
    '''
    Return the Raspberry Pi model
    https://www.raspberrypi-spy.co.uk/2012/09/checking-your-raspberry-pi-board-version/
    '''
    revision = os.popen("cat /proc/cpuinfo|grep '^Revision'|awk '{print $3}'").read().splitlines()
    return(revision[0])
