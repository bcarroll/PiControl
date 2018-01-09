# coding=utf8
import os
import sys
import sqlite3
from time import time
import datetime
from pprint import pprint
from flask import jsonify

from lib._logging import logger
from lib.pi_model import pi_model

def update_node(ipaddress, hostname, revision, serialnumber, last_checkin, database_file='db/PiControl.db'):
    logger.debug("Updating node: ipaddress=" + str(ipaddress) + ", hostname=" + str(hostname) + ", revision=" + str(revision) + ", serialnumber=" + str(serialnumber) +", last_checkin=" + str(last_checkin))
    if ipaddress == '127.0.0.1':
        return
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT ipaddress FROM nodes WHERE ipaddress={0}'.format("'{}'".format(ipaddress)))
            results = cursor.fetchone()
            if results:
                try:
                    logger.debug('Updating node (' + hostname + ':' + ipaddress + ') in nodes table.')
                    cursor.execute('UPDATE nodes set ipaddress={0}, hostname={1}, revision={2}, serialnumber={3}, last_checkin={4} WHERE ipaddress={0}'.format("'{}'".format(ipaddress), "'{}'".format(hostname), "'{}'".format(revision), "'{}'".format(serialnumber), last_checkin))
                except Exception as e:
                    logger.error('Error updating node (' + str(hostname) + ':' + str(ipaddress) + ') in nodes table. ' + e.message)
                    return()
            else:
                try:
                    logger.info('Node (' + hostname + ':' + ipaddress + ') does not exist in nodes table.  Inserting...')
                    cursor.execute('INSERT INTO nodes (ipaddress, hostname, revision, serialnumber, last_checkin) VALUES ({0},{1},{2},{3},{4})'.format("'{}'".format(ipaddress), "'{}'".format(hostname), "'{}'".format(revision), "'{}'".format(serialnumber), last_checkin))
                except Exception as e:
                    logger.error('Error inserting node (' + str(hostname) + ':' + str(ipaddress) + ') in nodes table. ' + e.message)
                    return()
        except Exception as e:
            logger.error(e.message)
            return()
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Exception as e:
        logger.error(e.message)
        return()

def update_config(beacon_port, beacon_interval, secret_key, log_level, log_file, log_files_backup, log_file_size, database_file='db/PiControl.db'):
    #logger.debug('Updating config: beacon_port=' + str(beacon_port) + ', beacon_interval=' + str(beacon_interval) + ', secret_key=' + str(secret_key) + ', log_level=' + str(log_level) + ', log_file=' + str(log_file) + ', log_files_backup=' + str(log_files_backup) + ', log_file_size=' + str(log_file_size))
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE config set beacon_port={0}, beacon_interval={1}, secret_key={2}, log_level={3}, log_file={4}, log_files_backup={5}, log_file_size={6} WHERE id=?'.format('active', beacon_port, beacon_interval, "'{}'".format(secret_key), log_level, "'{}'".format(log_file), log_files_backup, log_file_size))
        except Exception as e:
            logger.error(e.message)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Exception as e:
        logger.error(e.message)

#MOVED TO database_config.py
# def get_config(database_file='db/PiControl.db'):
#     '''
#     Returns PiControl configuration (from the PiControl database) in JSON
#     '''
#     logger.debug('get_config() called...')
#     try:
#         conn = sqlite3.connect(database_file)
#         cursor = conn.cursor()
#         try:
#             cursor.execute('SELECT beacon_port,beacon_interval,secret_key,log_level,log_file,log_files_backup,log_file_size FROM config WHERE id=?', ("active",))
#             results = cursor.fetchone()
#             config = {
#                     "beacon_port": results[0],
#                     "beacon_interval": results[1],
#                     "secret_key": results[2],
#                     "log_level": results[3],
#                     "log_file": results[4],
#                     "log_files_backup": results[5],
#                     "log_file_size": results[6]
#                 }
#             # Close the database connection
#             conn.close()
#             return (config)
#         except Exception as (e):
#             logger.error(e)
#     except Exception as e:
#         logger.error(e)

def get_nodes(database_file='db/PiControl.db'):
    logger.debug('get_nodes() called...')
    nodes = []
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        cursor.execute("SELECT ipaddress, hostname, revision, serialnumber, last_checkin FROM nodes")
        rows = cursor.fetchall()
        for row in rows:
            model = pi_model(row[2], type="dict")
            try:
                nodes.append({
                        "ipaddress": row[0],
                        "hostname": row[1],
                        "revision": row[2],
                        "model": model['model'],
                        "serialnumber": row[3],
                        "last_checkin": datetime.datetime.fromtimestamp(row[4]).strftime('%c')
                    })
            except:
                logger.error('nodes.append failed')
    except Exception as (e):
        logger.error(e)
    return jsonify({'nodes': nodes})
