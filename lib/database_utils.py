# coding=utf8
import os
import sys
import sqlite3
import datetime
import logging

from flask import jsonify
from time import time

from lib._logging import logger, get_logging_level
from lib.pi_model import pi_model

def check_db(database_file='db/PiControl.db'):
    if os.path.isfile(database_file):
        pass
    else:
        logger.critical('PiControl Database does not exist.')
        sys.exit()

def update_node(ipaddress, hostname, revision, serialnumber, secret_key, last_checkin, database_file='db/PiControl.db'):
    check_db()
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
                    cursor.execute('UPDATE nodes set ipaddress={0}, hostname={1}, revision={2}, serialnumber={3}, secret_key={4} last_checkin={5} WHERE ipaddress={0}'.format("'{}'".format(ipaddress), "'{}'".format(hostname), "'{}'".format(revision), "'{}'".format(serialnumber), "'{}'".format(secret_key), last_checkin))
                except Exception as e:
                    logger.error('Error updating node (' + str(hostname) + ':' + str(ipaddress) + ') in nodes table. ' + e.message)
                    return()
            else:
                try:
                    logger.info('Node (' + hostname + ':' + ipaddress + ') does not exist in nodes table.  Inserting...')
                    cursor.execute('INSERT INTO nodes (ipaddress, hostname, revision, serialnumber, secret_key, last_checkin) VALUES ({0},{1},{2},{3},{4},{5})'.format("'{}'".format(ipaddress), "'{}'".format(hostname), "'{}'".format(revision), "'{}'".format(serialnumber), "'{}'".format(secret_key), last_checkin))
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

def update_config(_beacon_port, _beacon_interval, _secret_key, _log_level, _log_file, _log_files_backup, _log_file_size, _beacon_listener_enabled, _beacon_sender_enabled, _background_charts_enabled, database_file='db/PiControl.db'):
    check_db()
    beacon_port               = _beacon_port[0]
    beacon_interval           = _beacon_interval[0]
    secret_key                = _secret_key[0]
    log_level                 = _log_level[0]
    log_file                  = _log_file[0]
    log_files_backup          = _log_files_backup[0]
    log_file_size             = _log_file_size[0]
    beacon_listener_enabled   = _beacon_listener_enabled[0]
    beacon_sender_enabled     = _beacon_sender_enabled[0]
    background_charts_enabled = _background_charts_enabled[0]
    logger.debug('Updating config: beacon_port=' + str(beacon_port) + ', beacon_interval=' + str(beacon_interval) + ', secret_key=' + str(secret_key) + ', log_level=' + str(log_level) + ', log_file=' + str(log_file) + ', log_files_backup=' + str(log_files_backup) + ', log_file_size=' + str(log_file_size), 'beacon_listener_enabled=' + str(beacon_listener_enabled), 'beacon_sender_enabled=' + str(beacon_sender_enabled), 'background_charts_enabled=' + str(background_charts_enabled))
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE config set beacon_port={0}, beacon_interval={1}, secret_key={2}, log_level={3}, log_file={4}, log_files_backup={5}, log_file_size={6}, beacon_listener_enabled={7}, beacon_sender_enabled={8}, background_charts_enabled={9} WHERE id="active"'.format(int(beacon_port), int(beacon_interval), "'{}'".format(secret_key), int(log_level), "'{}'".format(log_file), int(log_files_backup), int(log_file_size), int(beacon_listener_enabled), int(beacon_sender_enabled), int(background_charts_enabled)))
        except Exception as e:
            logger.error(e.message)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
        logging.getLogger('lib._logging').setLevel(get_logging_level(log_level))
        #logger.setLevel(get_logging_level(log_level))
    except Exception as e:
        logger.error(e.message)

def get_nodes(database_file='db/PiControl.db'):
    check_db()
    logger.debug('get_nodes() called...')
    nodes = []
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        cursor.execute("SELECT ipaddress, hostname, revision, serialnumber, secret_key, last_checkin FROM nodes")
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
                        "secret_key": row[4],
                        "last_checkin": datetime.datetime.fromtimestamp(row[5]).strftime('%c')
                    })
            except:
                logger.error('nodes.append failed')
    except Exception as (e):
        logger.error(e)
    return jsonify({'nodes': nodes})
