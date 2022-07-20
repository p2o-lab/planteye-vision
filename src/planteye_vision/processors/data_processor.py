from abc import ABC, abstractmethod
import time
import logging


class DataProcessor(ABC):
    @abstractmethod
    def apply_processor(self, input_data):
        pass

    def execute(self, input_data):
        begin_time = time.time()
        logging.debug(f'Processor {self.name} ({self.type}) execution execution began')
        processor_result = self.apply_processor(input_data)
        exec_duration = time.time() - begin_time
        logging.info(f'Processor {self.name} ({self.type}) execution finished (exec time {exec_duration:.3f} s)')
        return processor_result


class NonConfigurableDataProcessor(DataProcessor):
    @abstractmethod
    def apply_processor(self, input_data):
        pass

    def execute(self, input_data):
        return super().execute(input_data)


class ConfigurableDataProcessor(DataProcessor):
    @abstractmethod
    def apply_configuration(self):
        pass

    @abstractmethod
    def apply_processor(self, input_data):
        pass

    def execute(self, input_data):
        return super().execute(input_data)

