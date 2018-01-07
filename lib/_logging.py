import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from lib.database_utils import get_config

log_level        = "40"
log_file         = "logs/PiControl.log"
log_format       = '[%(asctime)s][%(levelname)s][%(thread)s][%(name)s] %(message)s'
log_files_backup = 5
log_roll_size    = 1024

try:
    config            = get_config()
    log_level         = config['log_level']
    log_file          = config['log_file']
    #log_format       = config['log_format']
    #log_files_backup = config['log_files_backup']
    #log_role_size    = config['log_roll_size']
except:
    logging.error('Error getting configuration from PiControl database')

#Create log directory if it does not already exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except PermissionError:
        sys.exit("Error creating " + LOG_DIR + '. PERMISSION DENIED')

#######################################################################
#Setup logging
global logger
logger    = logging.getLogger(__name__)
logformat = logging.Formatter(log_format)

loglevels = {
    "50": logging.CRITICAL,
    "40": logging.ERROR,
    "30": logging.WARNING,
    "20": logging.INFO,
    "10": logging.DEBUG,
    "0": "NONE"
}

# Set the logging level
loglevel = ( loglevels[log_level] )

hander = logging.StreamHandler()

if log_level == "0":
    #Logging is disabled
    handler = logging.NullHandler()
else:
    handler = RotatingFileHandler(log_file, mode='a', maxBytes=log_roll_size, backupCount=log_files_backup)

handler.setFormatter(logformat)
logger.addHandler(handler)
logger.setLevel(loglevel)

def get_logger():
    global logger
    return(logger)
