#!/usr/bin/python

import os
import sys
import socket

from functools import wraps

from flask import Flask
from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import flash
from flask import escape

from threading import Thread

from lib.pi_netconnect import pi_discovery
from lib.utils import generate_ssl_cert
from lib.network_utilities import get_interfaces
from lib.pi_utilities import cpu_usage, cpu_temperature, cpu_frequency, cpu_voltage, av_codecs, disk_usage, disk_usage_summary, pi_revision, pi_model, process_list, gpio_info
from lib.mem_utils import memory_usage, memory_usage_json, memory_voltage_json, swap_usage, swap_usage_json, memory_split
from lib.pyDash import get_netstat, get_platform

# use PAM authentication - https://stackoverflow.com/questions/26313894/flask-login-using-linux-system-credentials
from simplepam import authenticate

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'RaspberryPi_3.14'

discovery_thread = Thread(target=pi_discovery)
discovery_thread.start()

def require_login(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'username' in session:
            return( f(*args, **kwargs) )
        else:
            return(render_template('login.html'))
    return wrapped

@app.route('/')
@require_login
def index():
    return( render_template('index.html') )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(str(username), str(password)):
            session['username'] = request.form['username']
            return ( redirect(url_for('index')) )
        else:
            return('Invalid username/password')
    else:
        return(render_template('login.html'))

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return( redirect(url_for('index')) )

@app.context_processor
def get_hostname():
    return(dict(HOSTNAME=socket.gethostname()))

@app.route('/disk')
@require_login
def disk_info():
    return( render_template('disk.html', user=escape(session['username'])) )

@app.route('/network')
@require_login
def network_info():
    return( render_template('network.html', user=escape(session['username'])) )

@app.route('/memory')
@require_login
def memory_info():
    return( render_template('memory.html', user=escape(session['username'])) )

@app.route('/video')
@require_login
def video_info():
    return( render_template('video.html', user=escape(session['username'])) )

@app.route('/locale')
@require_login
def locale_info():
    return( render_template('locale.html', user=escape(session['username'])) )

@app.route('/users')
@require_login
def user_info():
    return( render_template('user.html', user=escape(session['username'])) )

@app.route('/services')
@require_login
def service_info():
    return( render_template('service.html', user=escape(session['username'])) )

@app.route('/overview')
@require_login
def pi_overview():
    return( render_template('overview.html', user=escape(session['username'])) )

@app.route('/processes')
@require_login
def process_info():
    return( render_template('processes.html', user=escape(session['username'])) )

@app.route('/terminal')
@require_login
def terminal():
    return( render_template('terminal.html', user=escape(session['username'])) )

@app.route('/gpio')
@require_login
def gpio():
    return( render_template('gpio.html', user=escape(session['username'])) )


#####################################################################################

@app.route('/cpu/usage')
@require_login
def get_cpu_usage():
    return(cpu_usage())

@app.route('/cpu/temp')
@require_login
def get_cpu_temperature():
    return(cpu_temperature())

@app.route('/cpu/voltage')
@require_login
def get_cpu_voltage():
    return(cpu_voltage())

@app.route('/cpu/frequency')
@require_login
def get_cpu_frequency():
    return(cpu_frequency())

@app.route('/video/codecs')
@require_login
def get_av_codecs():
    return(av_codecs())

@app.route('/mem/split')
@require_login
def get_memory_split():
    return(memory_split())

@app.route('/mem/usage')
@require_login
def get_memory_usage():
    return(memory_usage())

@app.route('/mem/usage/json')
@require_login
def get_memory_usage_json():
    return(memory_usage_json())

@app.route('/mem/voltage/json')
@require_login
def get_memory_voltage_json():
    return(memory_voltage_json())

@app.route('/swap/usage')
@require_login
def get_swap_usage():
    return(swap_usage())

@app.route('/swap/usage/json')
@require_login
def get_swap_usage_json():
    return(swap_usage_json())

@app.route('/disk/usage')
@require_login
def get_disk_usage():
    return(disk_usage())

@app.route('/disk/usage_summary')
@require_login
def get_disk_usage_summary():
    return(disk_usage_summary())

@app.route('/model')
@require_login
def get_pi_model():
    return(pi_model(get_pi_revision()))

@app.route('/model/revision')
@require_login
def get_pi_revision():
    return(pi_revision())

@app.route('/processes/list')
@require_login
def get_process_list():
    return(process_list())

@app.route('/network/interfaces')
@require_login
def get_network_interfaces():
    return(get_interfaces())

@app.route('/network/netstat')
@require_login
def get_netstat_details():
    return(get_netstat())

@app.route('/platform')
@require_login
def platform():
    return(get_platform())

@app.route('/gpio/info')
@require_login
def get_gpio():
    return(gpio_info())

def generate_ssl_cert(cert='server.crt', key='server.key'):
    pass

if __name__ == '__main__':
    #Uncomment the following line to generate a new self-signed SSL certificate
    #generate_ssl_cert()
    context = ('SSL/server.crt', 'SSL/server.key')
    app.run(ssl_context=context, threaded=True, debug=True, host='0.0.0.0', port=31415)
