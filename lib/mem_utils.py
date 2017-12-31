# coding=utf8
import os
import re
import subprocess
from flask import jsonify

def memory_usage():
    '''
    Returns memory usage statistics
    '''
    output = subprocess.check_output(['free', '-o', '-h']).decode('utf-8')
    m = re.search('Mem:\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])', output)
    total_mem = used_mem = free_mem = shared_mem = buffers_mem = cached_mem = ""
    try:
        total_mem = m.group(1)
        used_mem = m.group(2)
        free_mem = m.group(3)
        shared_mem = m.group(4)
        buffers_mem = m.group(5)
        cached_mem = m.group(6)
    except:
        pass
    return('''<th class="heading"><i class="fas fa-microchip"></i> Memory</th><td><table class="table-hover" style="width:100%;"><tr><th>Total</th><td class="pull-right">''' + total_mem + '''</td></tr><tr><th>Used</th><td class="pull-right">''' + used_mem + '''</td></tr><tr><th>Free</th><td class="pull-right">''' + free_mem + '''</td></tr><tr><th>Shared</th><td class="pull-right">''' + shared_mem + '''</td></tr><tr><th>Buffers</th><td class="pull-right">''' + buffers_mem + '''</td></tr><tr><th>Cached</th><td class="pull-right">''' + cached_mem + '''</td></tr></table></td>''')

def memory_usage_json():
    '''
    Returns memory usage statistics in JSON
    '''
    output = subprocess.check_output(['free', '-o', '-h']).decode('utf-8')
    m = re.search('Mem:\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])', output)
    total_mem = used_mem = free_mem = shared_mem = buffers_mem = cached_mem = ""
    try:
        total_mem = m.group(1)
        used_mem = m.group(2)
        free_mem = m.group(3)
        shared_mem = m.group(4)
        buffers_mem = m.group(5)
        cached_mem = m.group(6)
    except:
        pass
    return jsonify(
    	total=total_mem,
    	used=used_mem,
    	free=free_mem,
    	shared=shared_mem,
    	buffers=buffers_mem,
    	cached=cached_mem,
    	)

def memory_voltage_json():
	'''
	Returns
	'''
	output = subprocess.check_output(['vcgencmd', 'measure_volts', 'sdram_c']).decode('utf-8')
	sdram_c = output.replace('volt=', '')
	output = subprocess.check_output(['vcgencmd', 'measure_volts', 'sdram_i']).decode('utf-8')
	sdram_i = output.replace('volt=', '')
	output = subprocess.check_output(['vcgencmd', 'measure_volts', 'sdram_p']).decode('utf-8')
	sdram_p = output.replace('volt=', '')
	return jsonify(
			sdram_c=sdram_c,
			sdram_i=sdram_i,
			sdram_p=sdram_p
		)

def swap_usage():
    '''
    Returns swap usage statistics
    '''
    output = subprocess.check_output(['free', '-o', '-h']).decode('utf-8')
    m = re.search('Swap:\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\\n', output)
    total_swap = used_swap = free_swap = ""
    try:
        total_swap = m.group(1)
        used_swap = m.group(2)
        free_swap = m.group(3)
    except:
        pass
    return('''<th class="heading"><i class="fas fa-hdd"></i> Swap</th><td><table class="table-hover" style="width:100%;"><tr><th>Total</th><td class="pull-right">''' + total_swap + '''</td></tr><tr><th>Used</th><td class="pull-right">''' + used_swap + '''</td></tr><tr><th>Free</th><td class="pull-right">''' + free_swap + '''</td></tr></table></td>''')

def swap_usage_json():
    '''
    Returns swap usage statistics in JSON
    '''
    output = subprocess.check_output(['free', '-o', '-h']).decode('utf-8')
    m = re.search('Swap:\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\s+([0-9\.]+[MKB])\\n', output)
    total_swap = used_swap = free_swap = ""
    try:
        total_swap = m.group(1)
        used_swap = m.group(2)
        free_swap = m.group(3)
    except:
        pass
    return jsonify(
	    	total=total_swap,
	    	used=used_swap,
	    	free=free_swap
    	)

def memory_split():
	output = subprocess.check_output(['vcgencmd', 'get_mem', 'arm']).decode('utf-8')
	arm = output.replace('arm=', '')
	output = subprocess.check_output(['vcgencmd', 'get_mem', 'gpu']).decode('utf-8')
	gpu = output.replace('gpu=', '')
	return jsonify(
			arm=arm,
			gpu=gpu
		)