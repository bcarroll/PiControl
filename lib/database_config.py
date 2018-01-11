# coding=utf-8
import os
import sys
import sqlite3

def check_db(database_file='db/PiControl.db'):
    if os.path.isfile(database_file):
        pass
    else:
        print('ERROR: PiControl Database does not exist.')
        sys.exit()

def get_config(database_file='db/PiControl.db'):
    '''
    Returns PiControl configuration (from the PiControl database) in JSON
    '''
    check_db()
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT beacon_port,beacon_interval,secret_key,log_level,log_file,log_files_backup,log_file_size,beacon_listener_enabled,beacon_sender_enabled,background_charts_enabled FROM config WHERE id=?', ("active",))
            results = cursor.fetchone()
            config = {
                    "beacon_port": results[0],
                    "beacon_interval": results[1],
                    "secret_key": results[2],
                    "log_level": results[3],
                    "log_file": results[4],
                    "log_files_backup": results[5],
                    "log_file_size": results[6],
                    "beacon_listener_enabled": int(results[7]),
                    "beacon_sender_enabled": int(results[8]),
                    "background_charts_enabled": int(results[9])
                }
            # Close the database connection
            conn.close()
            return (config)
        except Exception as e:
            print(e.message)
    except Exception as e:
        print(e.message)
