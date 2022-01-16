from abc import ABC, abstractmethod
import time
import logging


class Inlet(ABC):
    @abstractmethod
    def apply_configuration(self):
        pass

    @abstractmethod
    def retrieve_data(self):
        pass

    @abstractmethod
    def execute(self):
        begin_time = time.time()
        logging.debug('Inlet ' + self.name + ' (' + self.type + ') execution began')
        inlet_result = self.retrieve_data()
        end_time = time.time()
        exec_duration = end_time - begin_time
        logging.debug('Inlet ' + self.name + ' (' + self.type + ') execution finished, execution time:' + str(exec_duration))
        return inlet_result
