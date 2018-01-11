import os
import sqlite3

def create_database(database_file='db/PiControl.db'):
    '''
    Create a blank SQLite3 database

    Keyword Arguments:
        database_file {str} -- Path to the database file to create (default: {'../db/PiControl.db'})
    '''
    if os.path.isfile(database_file):
        pass
    else:
        print('Creating PiControl database')
        print("\n")
        print('####################################################################')
        print('If this is the first (or only) instance of PiControl on the network,')
        print(' enter a new passphrase to be used as the PiControl Secret Key.')
        print("\n")
        print('If you have already created a PiControl Secret Key passphrase on another ')
        print('Raspberry Pi on your network, enter that passphrase.')
        print('####################################################################')
        print("\n")
        secret_key = raw_input('Enter your PiControl Secret Key: ')
        while  secret_key == '':
            secret_key = raw_input('A Secret Key is required. Enter your PiControl Secret Key: ')
        print("\n")
    try:
        conn = sqlite3.connect(database_file)
        # Create PiControl database tables
        create_tables(conn, secret_key)
        # Commit changes
        conn.commit()
        # Close the database connection
        conn.close()
    except Exception as e:
        print('Error opening/creating database. ' + e.message)

def create_tables(connection, secret_key):
    '''
    Create PiControl database tables using the provided database connection

    Arguments:
        connection {sqlite3.Connection} -- A previously created sqlite3 database connection object
    '''
    try:
        print('Creating tables in PiControl database')
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS 'nodes' ('ipaddress' VARCHAR NOT NULL, 'hostname' VARCHAR NOT NULL, 'revision' VARCHAR NOT NULL, 'serialnumber' VARCHAR NOT NULL,'last_checkin' DATETIME NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS 'config' ('id' TEXT NOT NULL, 'beacon_port' INTEGER NOT NULL, 'beacon_interval' INTEGER NOT NULL, 'secret_key' TEXT NOT NULL, 'log_level' INTEGER NOT NULL, 'log_file' TEXT NOT NULL, 'log_files_backup' INTEGER NOT NULL, 'log_file_size' INTEGER NOT NULL, 'beacon_listener_enabled' INTEGER NOT NULL,'beacon_sender_enabled' INTEGER NOT NULL, 'background_charts_enabled' INTEGER NOT NULL)")
        create_config(cursor, secret_key)
    except Exception as e:
        print(e.message)

def create_config(cursor, secret_key):
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
        print('PiControl config table already exists.')
    except Exception as e:
        # No results.  Add the default configuration data
        print('Adding default configuration to the PiControl database.')
        try:
            cursor.execute("INSERT INTO 'config' ('id', 'beacon_port', 'beacon_interval', 'secret_key', 'log_level', 'log_file', 'log_files_backup', 'log_file_size', 'beacon_listener_enabled', 'beacon_sender_enabled', 'background_charts_enabled') VALUES ('active', 31415, 60, " + secret_key + ", 10, 'logs/PiControl.log', 5, 4096000, 1, 1, 1)")
        except Exception as e:
            print('Error adding default configuration to PiControl database. ' + e.message)

if __name__ == '__main__':
    create_database()
