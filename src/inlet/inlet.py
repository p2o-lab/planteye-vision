from abc import ABC, abstractmethod
from src.configuration.config_provider import ConfigProvider


class Inlet(ABC):
    @abstractmethod
    def import_configuration(self, config_provider: ConfigProvider):
        pass

    @abstractmethod
    def apply_configuration(self):
        pass

    @abstractmethod
    def retrieve_data(self):
        pass
