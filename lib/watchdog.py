# coding=utf8
# Watch background processes/threads
import threading
from time import sleep

from lib._logging import logger

class Watchdog():
    def __init__(self,interval=30):
        '''
        Initialize Watchdog

        Keyword Arguments:
            interval {number} -- time to sleep between checking watchlist (default: {30})
        '''
        logging.debug('Watchdog.__init__() called...')
        self.interval  = interval
        self.watchlist = []
        logging.info('Watchdog initialized')

    def addThread(self, thread):
        logging.debug('Watchdog.addThread(' + str(thread.name) + ') called...')
        if thread in self.watchlist:
            logging.warn(str(thread.name) + ' is already in watchlist.')
        else:
            self.watchlist.append(thread)
        logging.info('Thread added to watchlist: ' + str(thread.name))

    def stop(self):
        '''
        stop Watchdog loop thread
        '''
        logger.debug('Watchdog.stop() called...')
        logger.info('Stopping Watchdog thread')
        self.looping = False
        self.status  = "stopped"

    def start(self):
        '''
        start Watchdog loop thread
        '''
        logger.info('Starting Watchdog thread')
        logger.debug('Watchdog.start() called...')
        self.looping = True
        self.thread = threading.Thread(name='watchdog', target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        self.status  = "running"

    def _loop(self):
        '''
        Monitor status of application threads
        '''
        logger.debug( 'Watchdog._loop() started...' )
        #keep track of the ip addresses we have already scanned
        ip_list = []
        while self.looping:
            for thread in self.watchlist:
                logging.debug('Checking status of thread: ' + thread.name)
                #TODO... Check the status of the thread...
            sleep(self.interval)
