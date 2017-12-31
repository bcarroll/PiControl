import os
import sys
import socket

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

from lib.network_utilities import get_ip_address
from lib.pi_utilities import cpu_usage, cpu_temperature, cpu_frequency, cpu_voltage, av_codecs, disk_usage, disk_usage_summary, pi_model
from lib.mem_utils import memory_usage, memory_usage_json, memory_voltage_json, swap_usage, swap_usage_json, memory_split

# use PAM authentication - https://stackoverflow.com/questions/26313894/flask-login-using-linux-system-credentials
from simplepam import authenticate

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'raspberry'

@app.route('/')
def index():
    if 'username' in session:
        return( render_template('index.html', user=escape(session['username'])) )
    return(render_template('login.html'))

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

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return( redirect(url_for('index')) )

@app.context_processor
def get_hostname():
    return(dict(HOSTNAME=socket.gethostname()))

@app.route('/disk')
def disk_info():
    if 'username' in session:
        return( render_template('disk.html', user=escape(session['username'])) )
    return(render_template('login.html'))

@app.route('/network')
def network_info():
    if 'username' in session:
        return( render_template('network.html', user=escape(session['username'])) )
    return(render_template('login.html'))

@app.route('/memory')
def memory_info():
    if 'username' in session:
        return( render_template('memory.html', user=escape(session['username'])) )
    return(render_template('login.html'))

@app.route('/video')
def video_info():
    if 'username' in session:
        return( render_template('video.html', user=escape(session['username'])) )
    return(render_template('login.html'))

@app.route('/locale')
def locale_info():
    if 'username' in session:
        return( render_template('locale.html', user=escape(session['username'])) )
    return(render_template('login.html'))

@app.route('/users')
def user_info():
    if 'username' in session:
        return( render_template('user.html', user=escape(session['username'])) )
    return(render_template('login.html'))

@app.route('/services')
def service_info():
    if 'username' in session:
        return( render_template('service.html', user=escape(session['username'])) )
    return(render_template('login.html'))

@app.route('/overview')
def pi_overview():
    if 'username' in session:
        return( render_template('overview.html', user=escape(session['username'])) )
    return(render_template('login.html'))

#####################################################################################

@app.route('/cpu/usage')
def get_cpu_usage():
    return(cpu_usage())

@app.route('/cpu/temp')
def get_cpu_temperature():
    return(cpu_temperature())

@app.route('/cpu/voltage')
def get_cpu_voltage():
    return(cpu_voltage())

@app.route('/cpu/frequency')
def get_cpu_frequency():
    return(cpu_frequency())

@app.route('/video/codecs')
def get_av_codecs():
    return(av_codecs())

@app.route('/mem/split')
def get_memory_split():
    return(memory_split())

@app.route('/mem/usage')
def get_memory_usage():
    return(memory_usage())

@app.route('/mem/usage/json')
def get_memory_usage_json():
    return(memory_usage_json())

@app.route('/mem/voltage/json')
def get_memory_voltage_json():
    return(memory_voltage_json())

@app.route('/swap/usage')
def get_swap_usage():
    return(swap_usage())

@app.route('/swap/usage/json')
def get_swap_usage_json():
    return(swap_usage_json())

@app.route('/disk/usage')
def get_disk_usage():
    return(disk_usage())

@app.route('/disk/usage_summary')
def get_disk_usage_summary():
    return(disk_usage_summary())

@app.route('/model')
def get_pi_model():
    return(pi_model())

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=31415)