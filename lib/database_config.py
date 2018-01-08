# coding=utf-8

import sqlite3
from sqlite3 import Error

from lib._logging import logger

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
