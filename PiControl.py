#!/usr/bin/python

import os
import sys
import socket
import atexit
import signal
import logging
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
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy

from lib.database_utils import update_config, get_nodes
from lib.pi_netconnect import UDPBeacon, UDPBeaconListener
from lib.network_utilities import get_interfaces
from lib.pi_utilities import cpu_count, cpu_usage, cpu_temperature, cpu_frequency, cpu_voltage, av_codecs, disk_usage, disk_usage_summary, pi_revision, process_list, gpio_info, pi_serialnumber
from lib.pi_model import pi_model
from lib.mem_utils import memory_usage, memory_usage_json, memory_voltage_json, swap_usage, swap_usage_json, memory_split
from lib.pyDash import get_netstat, get_platform
from lib.database_config import get_config
from lib.chart_utils import PiControlChart
from lib._logging import logger, handler, werkzeug_handler, sqlalchemy_handler
from lib.node_utils import node_cpu_usage, node_cpu_temperature

# use PAM authentication - https://stackoverflow.com/questions/26313894/flask-login-using-linux-system-credentials
from simplepam import authenticate

logging.Formatter('[%(asctime)s][%(levelname)s][%(thread)s][%(name)s] %(message)s')

configuration = get_config()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'PiControl' #get_config()['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/PiControl.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
################################################
# Setup logging
app.logger.addHandler(handler)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logger.level)
werkzeug_logger.addHandler(werkzeug_handler)

sqlalchemy_logger = logging.getLogger('sqlalchemy')
sqlalchemy_logger.setLevel(logger.level)
sqlalchemy_logger.addHandler(sqlalchemy_handler)

################################################

if configuration['beacon_sender_enabled'] == 1:
    # Create a UDP Beacon sender
    pi_discovery = UDPBeacon()
    pi_discovery.start()

if configuration['beacon_listener_enabled'] == 1:
    # Create a UDP Beacon receiver
    pi_discoverer = UDPBeaconListener()
    pi_discoverer.start()

# Create background chart data collectors
if configuration['background_charts_enabled'] == 1:
    cpu_temperature_chart = PiControlChart(data_function=cpu_temperature, max_elements=10, args='fahrenheit')
    cpu_temperature_chart.start()
# END OF BACKGROUND CHART DATA COLLECTORS

def close_running_threads(signum=None, frame=None):
    logger.debug('close_running_threads() called with signal %s', signum)
    # Stop UDP Beacon sender thread
    if pi_discovery.status == 'running':
        pi_discovery.stop()
    # Stop UDP Beacon Listener thread
    if pi_discoverer.status == 'running':
        pi_discoverer.stop()
    # Stop all PiControlChart threads
    for chart_thread in PiControlChart.instances:
        #cpu_temperature_chart.stop()
        if chart_thread.status == 'running':
            chart_thread.stop()
    try:
        request.environ.get('werkzeug.server.shutdown')
        logger.debug('Shutting down werkzeug webserver')
    except:
        logger.debug('Error shutting down werkzeug webserver')
        pass
    logger.info('Exiting')
    sys.exit(0)

#stop threads when the application stops
atexit.register(close_running_threads)

#stop threads when the application is killed
signal.signal(signal.SIGINT, close_running_threads)

##########################################################
# Error pages
@app.errorhandler(403)
def forbidden(error):
    logger.debug('Returning 403 error page')
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    logger.debug('Returning 404 error page')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.debug('Returning 500 error page')
    return render_template('errors/500.html'), 500
##########################################################

def require_login(f):
    '''
    Decorator for routes that require a logged in session
    '''
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'username' in session:
            return( f(*args, **kwargs) )
        else:
            return(render_template('login.html'))
    return (wrapped)

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
            logger.info(str(username) + ' successfully logged in')
            return ( redirect(url_for('index')) )
        else:
            logger.info('Login failed for ' + str(username))
            flash('Invalid username/password', 'error')
            return(render_template('login.html'))
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

@app.route('/settings', methods=['GET','POST'])
@require_login
def configuration():
    if request.method == 'POST':
        beacon_port=request.form['beacon_port'],
        beacon_interval=request.form['beacon_interval'],
        secret_key=request.form['secret_key'],
        log_level=request.form['log_level'],
        log_file=request.form['log_file'],
        log_files_backup=request.form['log_files_backup'],
        log_file_size=request.form['log_file_size'],
        beacon_listener_enabled=request.form['beacon_listener_enabled'],
        beacon_sender_enabled=request.form['beacon_sender_enabled'],
        background_charts_enabled=request.form['background_charts_enabled']
        try:
            # Update database with new configuration
            update_config(beacon_port, beacon_interval, secret_key, log_level, log_file,log_files_backup,log_file_size,beacon_listener_enabled,beacon_sender_enabled,background_charts_enabled)
            flash('Configuration updated')
        except:
            flash('Error updating configuration', 'error')

    # Get current configuration from database
    configuration = get_config()
    return(render_template('config.html',
                beacon_port=configuration['beacon_port'],
                beacon_interval=configuration['beacon_interval'],
                secret_key=configuration['secret_key'],
                log_level=configuration['log_level'],
                log_file=configuration['log_file'],
                log_files_backup=configuration['log_files_backup'],
                log_file_size=configuration['log_file_size'],
                beacon_listener_enabled=configuration['beacon_listener_enabled'],
                beacon_sender_enabled=configuration['beacon_sender_enabled'],
                background_charts_enabled=configuration['background_charts_enabled']
           )
    )

@app.route('/nodes')
@require_login
def get_discovered_nodes():
    return(render_template('nodes.html'))

@app.route('/nodes/refresh')
@require_login
def refresh_discovered_nodes():
    return (get_nodes())

@app.route('/dashboard')
@require_login
def get_dashboard():
    return(render_template('dashboard.html'))

#####################################################################################

@app.route('/charts/cpu/temperature')
@require_login
def get_cpu_temperature_chart():
    if cpu_temperature_chart.status == 'running':
        return jsonify({"chart": {"title": "CPU Temperature", "labels": cpu_temperature_chart.labels, "data": cpu_temperature_chart.list}})
    else:
        return jsonify({"chart": {"title": "CPU Temperature DISABLED","labels": 'DISABLED',"data": 'DISABLED'}})


@app.route('/cpu/count')
@require_login
def get_cpu_count():
    return(cpu_count())

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

@app.route('/serialnumber')
@require_login
def get_pi_serialnumber():
    return(pi_serialnumber())

@app.route('/update/PiControl')
@require_login
def update_PiControl():
    os.popen('git pull')
    return jsonify(status=1)

@app.route('/update/PiControl/status')
@require_login
def update_PiControl_status():
    status = os.popen('git status|grep "Your branch is up-to-date with \'origin/master\'"').read()
    if status:
        return jsonify(status=0)
    else:
        return jsonify(status=1)

#################################
# Dashboard chart data
@app.route('/dashboard/cpu_usage')
#@require_login
def dashboard_cpu_usage():
    return(cpu_usage(per_cpu=False))

@app.route('/dashboard/nodes_cpu_usage')
#@require_login
def get_node_cpu_usage():
    return(node_cpu_usage())

@app.route('/dashboard/cpu_temperature')
#@require_login
def dashboard_cpu_temperature():
    return(cpu_temperature(type='text_fahrenheit'))

@app.route('/dashboard/nodes_cpu_temperature')
#@require_login
def get_node_cpu_temperature():
    return(node_cpu_temperature())

if __name__ == '__main__':
    context = ('SSL/server.crt', 'SSL/server.key')
    app.run(ssl_context=context, threaded=True, debug=False, host='0.0.0.0', port=31415)
