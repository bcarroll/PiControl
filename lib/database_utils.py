# coding=utf8
import os
import sys
import sqlite3
from sqlite3 import Error
from time import time
import datetime
from pprint import pprint
from flask import jsonify

from lib._logging import logger
from lib.pi_model import pi_model

def create_database(database_file='db/PiControl.db'):
    '''
    Create a blank SQLite3 database

    Keyword Arguments:
        database_file {str} -- Path to the database file to create (default: {'../db/PiControl.db'})
    '''
    try:
        logger.debug('create_database() called...')
        conn = sqlite3.connect(database_file)
        # Create PiControl database tables
        create_tables(conn)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Error as e:
        logging.error('Error opening/creating database. ' + e)

def create_tables(connection):
    '''
    Create PiControl database tables using the provided database connection

    Arguments:
        connection {sqlite3.Connection} -- A previously created sqlite3 database connection object
    '''
    try:
        logger.debug('create_tables() called...')
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS 'nodes' ('ipaddress' VARCHAR NOT NULL, 'hostname' VARCHAR NOT NULL, 'revision' VARCHAR NOT NULL, 'serialnumber' VARCHAR NOT NULL,'last_checkin' DATETIME NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS 'config' ('id' TEXT NOT NULL, 'beacon_port' INTEGER NOT NULL, 'beacon_interval' INTEGER NOT NULL, 'secret_key' TEXT NOT NULL, 'log_level' INTEGER NOT NULL, 'log_file' TEXT NOT NULL, 'log_files_backup' INTEGER NOT NULL, 'log_file_size' INTEGER NOT NULL)")
        create_config(cursor)
    except Error as e:
        logger.error(e)

def create_config(cursor):
    '''
    Insert default configuration to config table
    Silently catches the exception if the config data already exists

    Arguments:
        cursor {sqlite3.Cursor} -- A previsouly created sqlite3 cursor object
    '''
    logger.debug('create_config() called...')
    # Get all rows from the config database table
    cursor.execute("SELECT * FROM 'config'")
    #There should never be more than one row in the config table
    config_rows = cursor.fetchall()

    try:
        # If the config table already has data, we don't need to do anything
        t = config_rows[0]
        logger.debug('config table previously initialized.')
    except:
        # No results.  Add the default configuration data
        logger.info('Adding default configuration to the PiControl database.')
        try:
            cursor.execute("INSERT INTO 'config' ('id', 'beacon_port', 'beacon_interval', 'secret_key', 'log_level', 'log_file', 'log_files_backup', 'log_file_size') VALUES ('active', 31415, 60, 'PiControl', 10, 'logs/PiControl.log', 5, 4096000)")
        except:
            logger.error('Error adding default configuration to PiControl database. ')

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
                except:
                    logger.error('Error updating node (' + str(hostname) + ':' + str(ipaddress) + ') in nodes table.')
                    return()
            else:
                try:
                    logger.info('Node (' + hostname + ':' + ipaddress + ') does not exist in nodes table.  Inserting...')
                    cursor.execute('INSERT INTO nodes (ipaddress, hostname, revision, serialnumber, last_checkin) VALUES ({0},{1},{2},{3},{4})'.format("'{}'".format(ipaddress), "'{}'".format(hostname), "'{}'".format(revision), "'{}'".format(serialnumber), last_checkin))
                except:
                    logger.error('Error inserting node (' + str(hostname) + ':' + str(ipaddress) + ') in nodes table.')
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

def update_config(beacon_port, beacon_interval, secret_key, log_level, log_file, log_files_backup, log_file_size, database_file='db/PiControl.db'):
    logger.debug('Updating config: beacon_port=' + str(beacon_port) + ', beacon_interval=' + str(beacon_interval) + ', secret_key=' + str(secret_key) + ', log_level=' + str(log_level) + ', log_file=' + str(log_file) + ', log_files_backup=' + str(log_files_backup) + ', log_file_size=' + str(log_file_size))
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

def get_config(database_file='db/PiControl.db'):
    '''
    Returns PiControl configuration (from the PiControl database) in JSON
    '''
    logger.debug('get_config() called...')
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT beacon_port,beacon_interval,secret_key,log_level,log_file,log_files_backup,log_file_size FROM config WHERE id=?', ("active",))
            results = cursor.fetchone()
            config = {
                    "beacon_port": results[0],
                    "beacon_interval": results[1],
                    "secret_key": results[2],
                    "log_level": results[3],
                    "log_file": results[4],
                    "log_files_backup": results[5],
                    "log_file_size": results[6]
                }
            # Close the database connection
            conn.close()
            return (config)
        except Error as (e):
            logger.error(e)
    except Error as e:
        logger.error(e)

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
    except Error as (e):
        logger.error(e)
    return jsonify({'nodes': nodes})
