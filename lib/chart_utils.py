# coding=utf-8
import threading
from time import sleep

from lib._logging import logger
from lib.pi_utilities import cpu_temperature

class PiControlChart():
    instances = []
    def __init__(self, data_function, args=None interval=5, max_elements=60, fill_empty=True, fill_data=0):
        '''
        Arguments:
            data_function {function} -- Name of a function that will return data to be added to the chart
            interval {integer} -- Seconds between chart data updates
            max_elements {integer} -- Maximum number of elements in the list
        '''
        self.function     = data_function
        self.function_args= args
        self.interval     = interval
        self.list         = []
        self.max_elements = max_elements
        self.fill_empty   = fill_empty
        self.fill_data    = fill_data
        self.status       = "initialized"
        # Add chart to the list of PiControlChart instances
        PiControlChart.instances.append(self)

        logger.debug('PiControlChart_' + str(self.function.__name__) + ' initialized')

    def start(self):
        '''
        start chart loop thread
        '''
        logger.info('Starting PiControlChart_' + str(self.function.__name__) + ' thread')
        logger.debug('start() called...')
        self.looping       = True
        self.thread        = threading.Thread(name='PiControlChart_' + str(self.function.__name__), target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        self.status        = "running"

    def stop(self):
        '''
        stop chart loop thread
        '''
        logger.debug('stop() called...')
        logger.info('Stopping PiControlChart_' + str(self.function.__name__) + ' thread')
        self.looping = False
        self.status  = "stopped"

    def _loop(self):
        logger.debug( 'PiControlChart_' + str(self.function.__name__) + ' thread loop started')
        while self.looping:
            self.addData(self.function(self.function_args))
            print (self.list)
            sleep(self.interval)
        self.thread.join(1)

    def addData(self, data):
        '''
        Add new data to the end of a list
        Remove the first element to keep the list no bigger than self.max_elements

        Arguments:
            data {any} -- Data to be appended to the list
            fill_empty {boolean} -- Fill empty elements in the list with fill_data
            fill_data {any} -- Value to use when filling the list
        '''
        logger.debug('addData(' + str(data) + ') called')
        if self.fill_empty and self.max_elements > len(self.list):
            while self.max_elements-1 > len(self.list):
                self.list.append(self.fill_data)
        if len(self.list) == self.max_elements:
            self.list.pop(0)
        self.list.append(data)
