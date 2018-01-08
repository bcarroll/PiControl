# coding=utf8
import os
import sys
import sqlite3
from sqlite3 import Error
from time import time
import datetime
from pprint import pprint
from flask import jsonify
import logging
from logging.handlers import RotatingFileHandler

from lib.pi_utilities import pi_model

def create_database(app_dir='./'):
    '''
    Create a blank SQLite3 database

    Keyword Arguments:
        app_dir {str} -- Path to PiControl base directory (default: {'./'})
        database_file {str} -- Path to the database file to create (default: {'PiControl.db'})
    '''
    database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../db/PiControl.db')
    try:
        conn = sqlite3.connect(database_file)
        # Create PiControl database tables
        create_tables(conn, app_dir)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Error as e:
        logger.error(e)

def create_tables(connection, app_dir):
    '''
    Create PiControl database tables using the provided database connection

    Arguments:
        connection {sqlite3.Connection} -- A previously created sqlite3 database connection object
    '''
    database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../db/PiControl.db')
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS 'nodes' ('ipaddress' VARCHAR NOT NULL, 'hostname' VARCHAR NOT NULL, 'revision' VARCHAR NOT NULL, 'serialnumber' VARCHAR NOT NULL,'last_checkin' DATETIME NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS 'config' ('id' TEXT NOT NULL, 'app_dir' TEXT NOT NULL, 'database_file' TEXT NOT NULL, 'beacon_port' INTEGER NOT NULL, 'beacon_interval' INTEGER NOT NULL, 'secret_key' TEXT NOT NULL, 'log_level' INTEGER NOT NULL, 'log_file' TEXT NOT NULL, 'log_files_backup' INTEGER NOT NULL, 'log_file_size' INTEGER NOT NULL)")
        create_config(cursor, app_dir)
    except Error as e:
        logger.error(e)

def create_config(cursor, app_dir):
    '''
    Insert default configuration to config table
    Silently catches the exception if the config data already exists

    Arguments:
        cursor {sqlite3.Cursor} -- A previsouly created sqlite3 cursor object
    '''
    database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../db/PiControl.db')
    try:
        # Get all rows from the config database table
        cursor.execute("SELECT * FROM 'config' WHERE id='active'")
        #There should never be more than one row in the config table
        config_rows = cursor.fetchall()
    except:
        logger.error('Error writing default config data')
    try:
        # If the config table already has data, we don't need to do anything
        t = config_rows[0]
        logger.debug('config table previously initialized.')
    except:
        # No results.  Add the default configuration data
        logger.info('Adding default configuration to the PiControl database.')
        try:
            cursor.execute("INSERT INTO 'config' ('id', 'app_dir', 'database_file', beacon_port', 'beacon_interval', 'secret_key', 'log_level', 'log_file', 'log_files_backup', 'log_file_size') VALUES ('active', " + app_dir + "," + database_file + ",31415, 60, 'PiControl', 10, '" + os.path.join('logs','PiControl.log') + "', 5, 4096000)")
        except Error as (e):
            logger.error('Error adding default configuration to PiControl database. ' + str(e))

def update_node(ipaddress, hostname, revision, serialnumber, last_checkin):
    logger.debug("Updating node: ipaddress=" + str(ipaddress) + ", hostname=" + str(hostname) + ", revision=" + str(revision) + ", serialnumber=" + str(serialnumber) +", last_checkin=" + str(last_checkin))
    database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../db/PiControl.db')
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
                except Error as (e):
                    logger.error(str(e))
                    return()
            else:
                try:
                    logger.info('Node (' + hostname + ':' + ipaddress + ') does not exist in nodes table.  Inserting...')
                    cursor.execute('INSERT INTO nodes (ipaddress, hostname, revision, serialnumber, last_checkin) VALUES ({0},{1},{2},{3},{4})'.format("'{}'".format(ipaddress), "'{}'".format(hostname), "'{}'".format(revision), "'{}'".format(serialnumber), last_checkin))
                except Error as (e):
                    logger.error(e)
                    return()
        except Error as (e):
            logger.error(e)
            return()
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Error as e:
        logger.error(e)
        return()

def update_config(beacon_port, beacon_interval, secret_key, log_level, log_file, log_files_backup, log_file_size):
    logger.debug('Updating config: beacon_port=' + str(beacon_port) + ', beacon_interval=' + str(beacon_interval) + ', secret_key=' + str(secret_key) + ', log_level=' + str(log_level) + ', log_file=' + str(log_file) + ', log_files_backup=' + str(log_files_backup) + ', log_file_size=' + str(log_file_size))
    database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../db/PiControl.db')
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE config set (beacon_port={0}, beacon_interval={1}, secret_key={2}, log_level={3}, log_file={4}, log_files_backup={5}, log_file_size={6}) WHERE id="active"'.format(beacon_port, beacon_interval, "'{}'".format(secret_key), log_level, "'{}'".format(log_file), log_files_backup, log_file_size))
        except Error as (e):
            logger.error(e)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Error as e:
        logger.error(e)

def get_config():
    '''
    Returns PiControl configuration (from the PiControl database) in JSON
    '''
    database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../db/PiControl.db')
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT app_dir,database_file,beacon_port,beacon_interval,secret_key,log_level,log_file,log_files_backup,log_file_size FROM config WHERE id=?', ("active",))
            results = cursor.fetchone()
            config = {
                    "app_dir": results[0],
                    "database_file": results[1],
                    "beacon_port": results[2],
                    "beacon_interval": results[3],
                    "secret_key": results[4],
                    "log_level": results[5],
                    "log_file": results[6],
                    "log_files_backup": results[7],
                    "log_file_size": results[8]
                }
            # Close the database connection
            conn.close()
            return (config)
        except Error as (e):
            logger.error(e)
    except Error as e:
        logger.error(e)

def get_nodes():
    nodes = []
    database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../db/PiControl.db')
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
    except Error as (e):
        logger.error(e)
    return jsonify({'nodes': nodes})


###############################################################################
# Logging workaround
log_level        = 10
log_file         = database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),'../logs/PiControl_database_utils.log')
log_format       = '[%(asctime)s][%(levelname)s][%(thread)s][%(name)s] %(message)s'
log_files_backup = 5
log_file_size    = 4096000

try:
    config            = get_config()
    log_level         = int(config['log_level'])
    log_file          = str(config['log_file'])
    log_format       = str(config['log_format'])
    log_files_backup = int(config['log_files_backup'])
    log_role_size    = int(config['log_file_size'])
except:
    logging.error('Error getting configuration from PiControl database')

#######################################################################
#Setup logging
logger    = logging.getLogger(__name__)
logformat = logging.Formatter('[%(asctime)s][%(levelname)s][%(thread)s][%(name)s] %(message)s')

loglevels = {
    50: logging.CRITICAL,
    40: logging.ERROR,
    30: logging.WARNING,
    20: logging.INFO,
    10: logging.DEBUG,
    0: "NONE"
}

# Set the logging level
loglevel = ( loglevels[log_level] )

handler = RotatingFileHandler(log_file, mode='a', maxBytes=log_file_size, backupCount=log_files_backup)

if log_level == 0:
    #Logging is disabled
    handler = logging.NullHandler()
    print ('Logging is disabled')

handler.setFormatter(logformat)
logger.addHandler(handler)
logger.setLevel(loglevel)
