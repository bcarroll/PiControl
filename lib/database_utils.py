import sqlite3
from sqlite3 import Error

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
        print(e)

def create_tables(connection):
    '''
    Create PiControl database tables using the provided database connection

    Arguments:
        connection {sqlite3.Connection} -- A previously created sqlite3 database connection object
    '''
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS 'nodes' ('ipaddress' VARCHAR NOT NULL, 'hostname' VARCHAR NOT NULL, 'revision' VARCHAR NOT NULL, 'last_checkin' DATETIME NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS 'config' ('beacon_port' INTEGER NOT NULL, 'beacon_interval' INTEGER NOT NULL, 'secret_key' TEXT NOT NULL, 'log_level' INTEGER NOT NULL, 'log_file' TEXT NOT NULL)")
        create_config(cursor)
    except Error as e:
        print(e)

def create_config(cursor):
    '''
    Insert default configuration to config table
    Silently catches the exception if the config data already exists

    Arguments:
        cursor {sqlite3.Cursor} -- A previsouly created sqlite3 cursor object
    '''
    try:
        cursor.execute("INSERT INTO 'config' ('beacon_port', 'beacon_interval', 'secret_key', 'log_level', 'log_file') VALUES (31415, 60, 'PiControl', 1, 'logs/PiControl.log')")
    except sqlite3.IntegrityError:
        pass

def update_node(database_file='db/PiControl.db', ipaddress, hostname, revision, last_checkin):
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO 'nodes' ('ipaddress', 'hostname', 'revision', 'last_checkin') VALUES (" + ipaddress + "," + hostname + "," + "," + revision + "," + last_checking + ")")
        except sqlite3.IntegrityError:
            cursor.execute("UPDATE 'nodes' set ('ipaddress'=" + ipaddress + ", 'hostname='" + hostname + ", 'revision='" + revision + ", 'last_checkin='" + last_checkin + ")")
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Error as e:
        print(e)

