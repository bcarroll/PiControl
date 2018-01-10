# coding=utf-8
import threading
from time import sleep, time, localtime, strftime

from datetime import datetime

from lib._logging import logger
from lib.pi_utilities import cpu_temperature

class PiControlChart():
    instances = []
    def __init__(self, data_function=None, args=None, labels='datetime', datetime_format='%b %d %I:%M:%S %p', interval=5, max_elements=60, fill_empty=True, fill_data=0):
        '''
        Arguments:
            data_function {function} -- Name of a function that will return data to be added to the chart (default: None)
            labels {string|None} -- Add labels to the data with a formatted datetime string (default: 'datetime')
            datetime_format {string} -- datetime format in strftime format (default: '%b %d %I:%M:%S %p')
            interval {integer} -- Seconds between chart data updates (default: 5)
            max_elements {integer} -- Maximum number of elements in the list (default: 60)
            fill_empty {boolean} -- Fill empty datapoints with data, when the chart is created (default: True)
            fill_data {data} -- Data to fill empty data points with (default: 0)

        '''
        self.function     = data_function
        self.function_args= args
        self.labels       = labels
        self.date_format  = datetime_format
        self.interval     = interval
        self.list         = []
        if labels == 'datetime':
            self.labels   = []
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
        # Fill beginning of the list
        logger.debug('addData(' + str(data) + ') called')
        if self.fill_empty and self.max_elements > len(self.list):
            previous_label_offset = self.interval
            while self.max_elements-1 > len(self.list):
                self.list.append(self.fill_data)
                if self.labels:
                    # fill the list with time labels
                    self.labels.append(strftime( self.datetime_format, localtime( int(time()) - previous_label_offset ) ))
                    previous_label_offset = previous_label_offset + self.interval

        if len(self.list) == self.max_elements:
            self.list.pop(0)
            if self.labels:
                self.labels.pop(0)
        # Add new data to the list
        self.list.append(data)
        self.labels.append( strftime( self.datetime_format, localtime( int( time() ) ) ) )

