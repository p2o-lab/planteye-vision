from abc import ABC, abstractmethod

from src.configuration.config_provider import ConfigProvider


class DataProcessor (ABC):
    @abstractmethod
    def apply_processor(self, input_data):
        pass


class NonConfigurableDataProcessor (DataProcessor):
    @abstractmethod
    def apply_processor(self, input_data):
        pass


class ConfigurableDataProcessor (DataProcessor):
    @abstractmethod
    def import_configuration(self, config_provider: ConfigProvider):
        pass

    @abstractmethod
    def apply_configuration(self):
        pass

    @abstractmethod
    def apply_processor(self, input_data):
        pass
