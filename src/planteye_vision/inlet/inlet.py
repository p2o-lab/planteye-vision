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
        logging.debug(f'Inlet {self.name} ({self.type}) execution began')
        inlet_result = self.retrieve_data()
        end_time = time.time()
        exec_duration = end_time - begin_time
        logging.info(f'Inlet {self.name} ({self.type}) execution finished (exec time {exec_duration:.3f} s)')
        return inlet_result
