import sqlite3
from sqlite3 import Error
from time import time
import logging

from flask import jsonify

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

def create_database(database_file='db/PiControl.db'):
    '''
    Create a blank SQLite3 database

    Keyword Arguments:
        database_file {str} -- Path to the database file to create (default: {'../db/PiControl.db'})
    '''
    try:
        conn = sqlite3.connect(database_file)
        # Create PiControl database tables
        create_tables(conn)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Error as e:
        logging.error(e)

def create_tables(connection):
    '''
    Create PiControl database tables using the provided database connection

    Arguments:
        connection {sqlite3.Connection} -- A previously created sqlite3 database connection object
    '''
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS 'nodes' ('ipaddress' VARCHAR NOT NULL, 'hostname' VARCHAR NOT NULL, 'revision' VARCHAR NOT NULL, 'last_checkin' DATETIME NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS 'config' ('id' TEXT NOT NULL, 'beacon_port' INTEGER NOT NULL, 'beacon_interval' INTEGER NOT NULL, 'secret_key' TEXT NOT NULL, 'log_level' INTEGER NOT NULL, 'log_file' TEXT NOT NULL)")
        create_config(cursor)
    except Error as e:
        logging.error(e)

def create_config(cursor):
    '''
    Insert default configuration to config table
    Silently catches the exception if the config data already exists

    Arguments:
        cursor {sqlite3.Cursor} -- A previsouly created sqlite3 cursor object
    '''
    # Get all rows from the config database table
    cursor.execute("SELECT * FROM 'config'")
    #There should never be more than one row in the config table
    config_rows = cursor.fetchall()

    try:
        # If the config table already has data, we don't need to do anything
        t = config_rows[0]
        logging.debug('config table previously initialized.')
    except:
        # No results.  Add the default configuration data
        logging.info('Adding default configuration to the PiControl database.')
        try:
            cursor.execute("INSERT INTO 'config' ('id', 'beacon_port', 'beacon_interval', 'secret_key', 'log_level', 'log_file') VALUES ('active', 31415, 60, 'PiControl', 30, 'logs/PiControl.log')")
        except Error as (e):
            logging.error('Error adding default configuration to PiControl database. ' + str(e))

def update_node(ipaddress, hostname, revision, last_checkin, database_file='db/PiControl.db'):
    logging.debug("Updating node: ipaddress=" + str(ipaddress) + ", hostname=" + str(hostname) + ", revision=" + str(revision) + ", last_checkin=" + str(last_checkin))
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE nodes set (ipaddress={0}, hostname={1}, revision={2}, last_checkin={3})'.format("'{}'".format(ipaddress), "'{}'".format(hostname), "'{}'".format(revision), last_checkin))
        except:
            try:
                cursor.execute('INSERT INTO nodes (ipaddress, hostname, revision, last_checkin) VALUES ({0},{1},{2},{3})'.format("'{}'".format(ipaddress), "'{}'".format(hostname), "'{}'".format(revision), last_checkin))
            except Error as (e):
                logging.error(e)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Error as e:
        logging.error(e)

def update_config(beacon_port, beacon_interval, secret_key, log_level, log_file, database_file='db/PiControl.db'):
    logging.debug('Updating config: beacon_port=' + str(beacon_port) + ', beacon_interval=' + str(beacon_interval) + ', secret_key=' + str(secret_key) + ', log_level=' + str(log_level) + ', log_file=' + str(log_file))
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE config set (beacon_port={0}, beacon_interval={1}, secret_key={2}, log_level={3}, log_file={4}) WHERE id=0'.format(beacon_port, beacon_interval, "'{}'".format(secret_key), log_level, "'{}'".format(log_file)))
        except Error as (e):
            logging.error(e)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Error as e:
        logging.error(e)

def get_config(database_file='db/PiControl.db'):
    '''
    Returns PiControl configuration (from the PiControl database) in JSON
    '''
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT beacon_port,beacon_interval,secret_key,log_level,log_file FROM config WHERE id=?', ("active",))
            results = cursor.fetchone()
            config = {
                    "beacon_port": results[0],
                    "beacon_interval": results[1],
                    "secret_key": results[2],
                    "log_level": results[3],
                    "log_file": results[4]
                }
            # Close the database connection
            conn.close()
            return (jsonify(config))
        except Error as (e):
            logging.error(e)
    except Error as e:
        logging.error(e)
